from sqlalchemy import String, DateTime, Boolean, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.session import Base
from typing import List, Optional
import datetime

class Domain(Base):
    __tablename__ = "domains"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    scans: Mapped[List["Scan"]] = relationship(back_populates="domain", cascade="all, delete-orphan")
    assets: Mapped[List["Asset"]] = relationship(back_populates="domain", cascade="all, delete-orphan")

class Scan(Base):
    __tablename__ = "scans"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    mode: Mapped[str] = mapped_column(String, default="quick")
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    total_found: Mapped[int] = mapped_column(default=0)
    new_count: Mapped[int] = mapped_column(default=0)
    
    domain: Mapped["Domain"] = relationship(back_populates="scans")
    observations: Mapped[List["Observation"]] = relationship(back_populates="scan", cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint('domain_id', 'subdomain', name='_domain_subdomain_uc'),)
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"), nullable=False)
    subdomain: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    first_seen_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    first_scan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("scans.id"))
    last_scan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("scans.id"))
    
    is_gone: Mapped[bool] = mapped_column(Boolean, default=False)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False)
    
    status_code: Mapped[Optional[int]] = mapped_column(nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    port: Mapped[Optional[int]] = mapped_column(nullable=True)
    cdn: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    webserver: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tech_stack: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    domain: Mapped["Domain"] = relationship(back_populates="assets")
    observations: Mapped[List["Observation"]] = relationship(back_populates="asset", cascade="all, delete-orphan")

class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (UniqueConstraint('scan_id', 'asset_id', name='_scan_asset_uc'),)
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    
    status_code: Mapped[Optional[int]] = mapped_column(nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    port: Mapped[Optional[int]] = mapped_column(nullable=True)
    cdn: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    webserver: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tech_stack: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    scan: Mapped["Scan"] = relationship(back_populates="observations")
    asset: Mapped["Asset"] = relationship(back_populates="observations")