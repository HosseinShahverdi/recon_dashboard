from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models import Asset, Scan

async def mark_gone_assets(db: AsyncSession, domain_id: int, current_scan_id: int):
    stmt = (
        update(Asset)
        .where(
            Asset.domain_id == domain_id,
            Asset.last_scan_id != current_scan_id,
            Asset.is_gone == False
        )
        .values(is_gone=True)
    )
    await db.execute(stmt)
    await db.commit()