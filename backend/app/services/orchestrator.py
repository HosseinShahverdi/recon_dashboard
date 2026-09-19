import asyncio
from app.scanners.subfinder import SubfinderScanner
from app.scanners.findomain import FindomainScanner
from app.scanners.assetfinder import AssetfinderScanner

REGISTRY = {
    "subfinder": SubfinderScanner,
    "findomain": FindomainScanner,
    "assetfinder": AssetfinderScanner,
}

PRESETS = {
    "quick": ["subfinder", "findomain"],
    "deep": ["subfinder", "findomain", "assetfinder"],
}

async def discover(domain: str, tools: list[str]) -> set[str]:
    scanners = [REGISTRY[t]() for t in tools if t in REGISTRY]
    results = await asyncio.gather(
        *(s.run(domain) for s in scanners),
        return_exceptions=True,
    )
    
    found: set[str] = set()
    for r in results:
        if isinstance(r, set):
            found |= r
    return {s for s in found if s == domain or s.endswith("." + domain)}