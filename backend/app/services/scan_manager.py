import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.db.session import async_session
from app.db.models import Scan, Domain, Asset, Observation
from app.services.orchestrator import discover, PRESETS
from app.scanners.httpx_probe import HttpxProbe
from app.scanners.dnsx_resolver import DnsxResolver
from app.services.wildcard import WildcardGuard

BACKGROUND_TASKS: set[asyncio.Task] = set()
BASE_KEYS = ["status_code", "scheme", "ip", "asn", "port", "length", "cname", "title", "webserver", "tech_stack", "cdn", "is_wildcard"]

def launch_scan(scan_id: int) -> asyncio.Task:
    task = asyncio.create_task(run_scan(scan_id))
    BACKGROUND_TASKS.add(task)
    task.add_done_callback(BACKGROUND_TASKS.discard)
    return task

async def run_scan(scan_id: int):
    async with async_session() as db:
        scan = await db.get(Scan, scan_id)
        domain = await db.get(Domain, scan.domain_id)
        scan.status = "running"
        await db.commit()

        tools = PRESETS.get(scan.mode, PRESETS["quick"])
        found = await discover(domain.name, tools)
        
        if not found:
            scan.status = "failed"
            scan.finished_at = datetime.now(timezone.utc)
            await db.commit()
            return

        wildcard_ips = await WildcardGuard().detect(domain.name)
        resolved = await DnsxResolver().resolve(sorted(found))
        enriched = await HttpxProbe().probe(sorted(found))

        new_count = 0
        for sub in sorted(found):
            stmt = select(Asset).where(Asset.domain_id == domain.id, Asset.subdomain == sub)
            asset = (await db.execute(stmt)).scalar_one_or_none()
            
            info = {k: None for k in BASE_KEYS}
            info.update(resolved.get(sub, {}))
            http_info = enriched.get(sub, {})
            info.update({k: v for k, v in http_info.items() if v is not None})
            info["tech_stack"] = info.get("tech_stack") or []
            info["is_wildcard"] = bool(info.get("ip")) and info.get("ip") in wildcard_ips

            if asset is None:
                asset = Asset(domain_id=domain.id, subdomain=sub, first_scan_id=scan.id, **info)
                new_count += 1
                db.add(asset)
            else:
                for key, val in info.items():
                    if hasattr(asset, key): setattr(asset, key, val)
                asset.is_gone = False

            await db.flush()
            db.add(Observation(scan_id=scan.id, asset_id=asset.id, **info))
            asset.last_seen_at = datetime.now(timezone.utc)
            asset.last_scan_id = scan.id

        scan.total_found = len(found)
        scan.new_count = new_count
        scan.status = "completed"
        scan.finished_at = datetime.now(timezone.utc)
        await db.commit()