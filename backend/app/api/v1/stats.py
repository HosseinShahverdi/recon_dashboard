from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Asset, Scan

router = APIRouter()

@router.get("/{domain_id}")
async def get_domain_stats(domain_id: int, db: AsyncSession = Depends(get_db)):
    def count(*conds):
        return select(func.count(Asset.id)).where(Asset.domain_id == domain_id, *conds)

    alive = Asset.is_gone == False  # noqa: E712

    total   = (await db.execute(count(alive))).scalar() or 0
    new     = (await db.execute(count(alive, Asset.first_scan_id == Asset.last_scan_id))).scalar() or 0
    gone    = (await db.execute(count(Asset.is_gone == True))).scalar() or 0  # noqa: E712
    live    = (await db.execute(count(alive, Asset.status_code.isnot(None)))).scalar() or 0
    cdn     = (await db.execute(count(alive, Asset.cdn.isnot(None)))).scalar() or 0
    ips     = (await db.execute(
        select(func.count(func.distinct(Asset.ip)))
        .where(Asset.domain_id == domain_id, Asset.ip.isnot(None))
    )).scalar() or 0
    scans   = (await db.execute(
        select(func.count(Scan.id)).where(Scan.domain_id == domain_id)
    )).scalar() or 0
    latest = (await db.execute(
        select(func.max(Scan.id)).where(Scan.domain_id == domain_id)
    )).scalar()

    return {
        "assets": total, "new": new, "gone": gone, "responding": live,
        "behind_cdn": cdn, "unique_ips": ips, "scans": scans,
        "latest_scan_id": latest,

    }