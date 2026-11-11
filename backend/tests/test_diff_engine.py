import pytest
import pytest_asyncio
from sqlalchemy import select
from app.db.models import Asset, Domain, Domain, Scan
from app.services.diff_engine import mark_gone_assets


@pytest.mark.asyncio
async def test_mark_gone_assets_marks_unseen_as_gone(test_db, sample_domain):
    """Assets not found in current scan should be marked as gone."""
    scan1 = Scan(domain_id=sample_domain.id, status="completed")
    test_db.add(scan1)
    await test_db.commit()
    await test_db.refresh(scan1)
    
    for sub in ["a.example.com", "b.example.com", "c.example.com"]:
        asset = Asset(
            domain_id=sample_domain.id,
            subdomain=sub,
            first_scan_id=scan1.id,
            last_scan_id=scan1.id
        )
        test_db.add(asset)
    await test_db.commit()
    
    # Create scan #2 (which found nothing)
    scan2 = Scan(domain_id=sample_domain.id, status="completed")
    test_db.add(scan2)
    await test_db.commit()
    await test_db.refresh(scan2)
    
    # Run diff engine
    await mark_gone_assets(test_db, sample_domain.id, scan2.id)
    
    # Verify all 3 assets are now marked as gone
    result = await test_db.execute(select(Asset).where(Asset.is_gone == True))
    gone_assets = result.scalars().all()
    assert len(gone_assets) == 3


@pytest.mark.asyncio
async def test_mark_gone_assets_keeps_current_assets_alive(test_db, sample_domain):
    """Assets found in current scan should NOT be marked as gone."""
    scan1 = Scan(domain_id=sample_domain.id, status="completed")
    test_db.add(scan1)
    await test_db.commit()
    await test_db.refresh(scan1)
    
    asset_a = Asset(
        domain_id=sample_domain.id,
        subdomain="a.example.com",
        first_scan_id=scan1.id,
        last_scan_id=scan1.id
    )
    test_db.add(asset_a)
    await test_db.commit()
    
    scan2 = Scan(domain_id=sample_domain.id, status="completed")
    test_db.add(scan2)
    await test_db.commit()
    await test_db.refresh(scan2)
    
    asset_a.last_scan_id = scan2.id
    await test_db.commit()
    
    await mark_gone_assets(test_db, sample_domain.id, scan2.id)
    
    await test_db.refresh(asset_a)
    assert asset_a.is_gone == False


@pytest.mark.asyncio
async def test_mark_gone_assets_revives_returning_assets(test_db, sample_domain):
    """Assets that disappear then reappear should be revived."""
    scan1 = Scan(domain_id=sample_domain.id, status="completed")
    scan2 = Scan(domain_id=sample_domain.id, status="completed")
    test_db.add_all([scan1, scan2])
    await test_db.commit()
    await test_db.refresh(scan1)
    await test_db.refresh(scan2)
    
    asset = Asset(
        domain_id=sample_domain.id,
        subdomain="api.example.com",
        first_scan_id=scan1.id,
        last_scan_id=scan1.id
    )
    test_db.add(asset)
    await test_db.commit()
    await test_db.refresh(asset)
    
    await mark_gone_assets(test_db, sample_domain.id, scan2.id)
    await test_db.refresh(asset)
    assert asset.is_gone == True
    
    scan3 = Scan(domain_id=sample_domain.id, status="completed")
    test_db.add(scan3)
    await test_db.commit()
    await test_db.refresh(scan3)
    
    asset.last_scan_id = scan3.id
    asset.is_gone = False  
    await test_db.commit()
    
    await mark_gone_assets(test_db, sample_domain.id, scan3.id)
    await test_db.refresh(asset)
    
    assert asset.is_gone == False


@pytest.mark.asyncio
async def test_mark_gone_assets_only_affects_target_domain(test_db, sample_domain):
    """Diff engine should only mark assets from the target domain."""
    other_domain = Domain(name="other.com")
    test_db.add(other_domain)
    await test_db.commit()
    await test_db.refresh(other_domain)
    
    scan1 = Scan(domain_id=sample_domain.id, status="completed")
    test_db.add(scan1)
    await test_db.commit()
    await test_db.refresh(scan1)
    
    asset_target = Asset(
        domain_id=sample_domain.id,
        subdomain="api.example.com",
        first_scan_id=scan1.id,
        last_scan_id=scan1.id
    )
    
    asset_other = Asset(
        domain_id=other_domain.id,
        subdomain="api.other.com",
        first_scan_id=scan1.id,
        last_scan_id=scan1.id
    )
    
    test_db.add_all([asset_target, asset_other])
    await test_db.commit()
    
    scan2 = Scan(domain_id=sample_domain.id, status="completed")
    test_db.add(scan2)
    await test_db.commit()
    await test_db.refresh(scan2)
    
    await mark_gone_assets(test_db, sample_domain.id, scan2.id)
    
    await test_db.refresh(asset_target)
    assert asset_target.is_gone == True
    
    await test_db.refresh(asset_other)
    assert asset_other.is_gone == False


@pytest.mark.asyncio
async def test_mark_gone_assets_no_effect_when_no_scans(test_db, sample_domain):
    """Diff engine should not crash when there are no prior scans."""
    await mark_gone_assets(test_db, sample_domain.id, 999)  # Non-existent scan ID
    
    result = await test_db.execute(select(Asset))
    assets = result.scalars().all()
    assert len(assets) == 0