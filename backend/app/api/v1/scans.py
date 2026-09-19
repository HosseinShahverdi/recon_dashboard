import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional

from app.db.session import get_db
from app.db.models import Scan, Domain, Asset, Observation
from app.services.scan_manager import launch_scan

router = APIRouter()

class ScanCreate(BaseModel):
    domain_id: int
    mode: str = "quick"
    
@router.post("/", status_code=202)
async def start_scan(payload: ScanCreate, db: AsyncSession = Depends(get_db)):
    domain = await db.get(Domain, payload.domain_id)
    if not domain:
        raise HTTPException(404, "Domain not found")
    
    scan = Scan(domain_id = payload.domain_id, mode=payload.mode, status="pending")
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    
    launch_scan(scan.id)
    return {"scan_id":scan.id, "status":"pending"}

@router.get("/{scan_id}")
async def scan_status(scan_id: int, db: AsyncSession=Depends(get_db)):
    scan = await db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(404, "scan not found")
    return {
        "id": scan.id, "status": scan.status, "mode": scan.mode,
        "total_found": scan.total_found, "new_count": scan.new_count,
        "started_at": scan.started_at, "finished_at": scan.finished_at,
    }
    
@router.get("/{scan_id}/results")
async def scan_results(scan_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Asset, Observation)
        .join(Observation, Observation.asset_id == Asset.id)
        .where(Observation.scan_id == scan_id)
        .order_by(Asset.subdomain)
    )
    rows = (await db.execute(stmt)).all()
    return [
        {"subdomain": a.subdomain, **{
            k: getattr(o, k) for k in
            ("status_code", "scheme", "ip", "port", "length", "cdn",
             "cname", "asn", "title", "webserver", "tech_stack")
        }}
        for a, o in rows
    ]