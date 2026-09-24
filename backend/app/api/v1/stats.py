from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.db.models import Asset

router = APIRouter()

@router.get("/{domain_id}")
async def get_domain_stats(domain_id: int, db: AsyncSession = Depends(get_db)):
    base_q = select(Asset).where(Asset.domain_id == domain_id)
    
    # Execute all stats concurrently (TEACH POINT: asyncio.gather with DB)
    total_q = select(func.count(Asset.id)).where(Asset.domain_id == domain_id, Asset.is_gone == False)
    new_q = select(func.count(Asset.id)).where(Asset.domain_id == domain_id, Asset.first_scan_id == Asset.last_scan_id, Asset.is_gone == False)
    live_q = select(func.count(Asset.id)).where(Asset.domain_id == domain_id, Asset.status_code.isnot(None), Asset.is_gone == False)
    cdn_q = select(func.count(Asset.id)).where(Asset.domain_id == domain_id, Asset.cdn.isnot(None), Asset.is_gone == False)
    
    r1 = await db.execute(total_q)
    r2 = await db.execute(new_q)
    r3 = await db.execute(live_q)
    r4 = await db.execute(cdn_q)
    
    return {
        "total_assets": r1.scalar() or 0,
        "new_assets": r2.scalar() or 0,
        "live_responding": r3.scalar() or 0,
        "behind_cdn": r4.scalar() or 0,
    }