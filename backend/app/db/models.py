from ast import For
from email.policy import default

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scans = relationship("Scan", back_populates="domain", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="domain", cascade="all, delete-orphan")

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    status = Column(String, default="pending") # pending, running, completed, failed
    mode = Column(String, default="quick")     # quick, deep
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    total_found = Column(Integer, default=0)
    new_count = Column(Integer, default=0)
    domain = relationship("Domain", back_populates="scans")
    observations = relationship("Observation", back_populates="scan", cascade="all, delete-orphan")


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint('domain_id', 'subdomain', name='_domain_subdomain_uc'),)

    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    subdomain = Column(String, nullable=False, index=True)
    
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    first_scan_id = Column(Integer, ForeignKey("scans.id"))
    last_scan_id = Column(Integer, ForeignKey("scans.id"))
    is_gone = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    
    # Cached latest enrichment 
    status_code = Column(Integer, nullable=True)
    ip = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    cdn = Column(String, nullable=True)
    title = Column(String, nullable=True)
    webserver = Column(String, nullable=True)
    tech_stack = Column(JSON, nullable=True)
    
    domain = relationship("Domain", back_populates="assets")
    observations = relationship("Observation", back_populates="asset", cascade="all, delete-orphan")

class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (UniqueConstraint('scan_id', 'asset_id', name='_scan_asset_uc'),)
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    status_code = Column(Integer, nullable=True)
    ip = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    cdn = Column(String, nullable=True)
    title = Column(String, nullable=True)
    webserver = Column(String, nullable=True)
    tech_stack = Column(JSON, nullable=True)
    
    scan = relationship("Scan", back_populates="observations")
    asset = relationship("Asset", back_populates="observations")
    