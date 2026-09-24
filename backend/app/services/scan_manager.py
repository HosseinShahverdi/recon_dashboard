import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import async_session
from app.db.models import Scan, Domain, Asset, Observation
from app.services.orchestrator import discover, PRESETS
from app.scanners.httpx_probe import HttpxProbe
from app.services.diff_engine import mark_gone_assets


# TEACH POINT: keep references to background tasks or Python may garbage-collect them mid-run
BACKGROUND_TASKS: set[asyncio.Task] = set()


def launch_scan(scan_id: int) -> asyncio.Task:
    task = asyncio.create_task(run_scan(scan_id))
    BACKGROUND_TASKS.add(task)
    task.add_done_callback(BACKGROUND_TASKS.discard)
    return task


async def run_scan(scan_id: int):
    # TEACH POINT: background tasks open their OWN db session.
    # Never reuse the request's session — it's already closed!
    async with async_session() as db:
        scan = await db.get(Scan, scan_id)
        domain = await db.get(Domain, scan.domain_id)

        scan.status = "running"
        await db.commit()

        tools = PRESETS.get(scan.mode, PRESETS["quick"])
        found = await discover(domain.name, tools)
        enriched = await HttpxProbe().probe(sorted(found))

        new_count = 0
        for sub in sorted(found):
            stmt = select(Asset).where(
                Asset.domain_id == domain.id, Asset.subdomain == sub
            )
            asset = (await db.execute(stmt)).scalar_one_or_none()
            info = enriched.get(sub, {})

            if asset is None:
                asset = Asset(domain_id=domain.id, subdomain=sub,
                              first_scan_id=scan.id, **info)
                new_count += 1
                db.add(asset)
            else:
                obs_only = {k: v for k, v in info.items() if hasattr(asset, k)}
                for key, val in obs_only.items():
                    setattr(asset, key, val)      # refresh cached latest values
                asset.is_gone = False

            await db.flush()                      # get asset.id before Observation
            db.add(Observation(scan_id=scan.id, asset_id=asset.id, **info))

            asset.last_seen_at = datetime.now(timezone.utc)
            asset.last_scan_id = scan.id

        scan.total_found = len(found)
        scan.new_count = new_count
        scan.status = "completed"
        scan.finished_at = datetime.now(timezone.utc)
        
        await mark_gone_assets(db, domain.id,scan.id)
        
        await db.commit()