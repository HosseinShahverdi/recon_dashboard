from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.db.models import Asset

router = APIRouter()


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subdomain: str
    status_code: Optional[int]
    scheme: Optional[str]
    ip: Optional[str]
    port: Optional[int]
    length: Optional[int]
    cdn: Optional[str]
    cname: Optional[str]
    asn: Optional[str]
    title: Optional[str]
    webserver: Optional[str]
    tech_stack: Optional[list]
    first_seen_at: datetime
    last_seen_at: datetime
    is_gone: bool
    is_starred: bool


@router.get("/", response_model=List[AssetOut])
async def list_assets(domain_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Asset).where(Asset.domain_id == domain_id).order_by(Asset.subdomain)
    return (await db.execute(stmt)).scalars().all()