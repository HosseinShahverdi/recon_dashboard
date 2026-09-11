from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Domain
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class DomainCreate(BaseModel):
    name: str

class DomainOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=DomainOut)
async def create_domain(domain_in: DomainCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(Domain).where(Domain.name == domain_in.name)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Domain already exists")
        
    new_domain = Domain(name=domain_in.name)
    db.add(new_domain)
    await db.commit()
    await db.refresh(new_domain)
    return new_domain

@router.get("/", response_model=list[DomainOut])
async def list_domains(db: AsyncSession = Depends(get_db)):
    stmt = select(Domain).order_by(Domain.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()