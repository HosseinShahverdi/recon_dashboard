from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.db.models import Asset

router = APIRouter()

class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    domain_id: int
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
    first_scan_id: Optional[int]
    last_scan_id: Optional[int]
    
    is_gone: bool
    is_starred: bool
    
    # Computed properties for the UI badges
    @property
    def is_new(self) -> bool:
        """A subdomain is 'new' if it has only been seen in one scan ever."""
        return self.first_scan_id == self.last_scan_id

    @property
    def status_class(self) -> str:
        """Returns '2xx', '3xx', '4xx', '5xx', or 'dead' for UI coloring."""
        if not self.status_code: return "dead"
        if 200 <= self.status_code < 300: return "2xx"
        if 300 <= self.status_code < 400: return "3xx"
        if 400 <= self.status_code < 500: return "4xx"
        if 500 <= self.status_code < 600: return "5xx"
        return "unknown"

@router.get("/", response_model=List[AssetOut])
async def list_assets(
    domain_id: int,
    status: Optional[str] = Query(None, description="2xx, 3xx, 4xx, 5xx, dead"),
    is_new: Optional[bool] = None,
    hide_gone: bool = Query(True, description="Hide subdomains not found in latest scan"),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Asset).where(Asset.domain_id == domain_id)

    # 1. Hide gone assets by default (can be toggled in UI)
    if hide_gone:
        stmt = stmt.where(Asset.is_gone == False)

    # 2. Status Code Filtering (The "Chips")
    if status == "2xx":
        stmt = stmt.where(Asset.status_code.between(200, 299))
    elif status == "3xx":
        stmt = stmt.where(Asset.status_code.between(300, 399))
    elif status == "4xx":
        stmt = stmt.where(Asset.status_code.between(400, 499))
    elif status == "5xx":
        stmt = stmt.where(Asset.status_code.between(500, 599))
    elif status == "dead":
        stmt = stmt.where(Asset.status_code.is_(None)) # httpx couldn't connect

    # 3. "New" Filtering
    if is_new is True:
        stmt = stmt.where(Asset.first_scan_id == Asset.last_scan_id)

    # 4. Text Search (searches subdomain, title, and IP)
    if search:
        search_term = f"%{search}%"
        stmt = stmt.where(
            or_(
                Asset.subdomain.ilike(search_term),
                Asset.title.ilike(search_term),
                Asset.ip.ilike(search_term),
            )
        )

    stmt = stmt.order_by(Asset.subdomain)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.patch("/{asset_id}/star")
async def toggle_star(asset_id: int, db: AsyncSession = Depends(get_db)):
    """Endpoint for the UI Star button."""
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise 404
    asset.is_starred = not asset.is_starred
    await db.commit()
    return {"id": asset.id, "is_starred": asset.is_starred}