import asyncio
from app.scanners.subfinder import SubfinderScanner
from app.scanners.findomain import FindomainScanner
from app.scanners.assetfinder import AssetfinderScanner
from app.scanners.shuffledns import ShufflednsScanner

REGISTRY = {
    "subfinder": SubfinderScanner, "findomain": FindomainScanner,
    "assetfinder": AssetfinderScanner, "shuffledns": ShufflednsScanner,
}
PRESETS = {
    "quick": ["subfinder", "findomain"],
    "deep": ["subfinder", "findomain", "assetfinder", "shuffledns"],
}

async def discover(domain: str, tools: list[str]) -> set[str]:
    scanners = [REGISTRY[t]() for t in tools if t in REGISTRY]
    results = await asyncio.gather(*(s.run(domain) for s in scanners), return_exceptions=True)
    found = set()
    for r in results:
        if isinstance(r, set): found |= r
    return {s for s in found if s == domain or s.endswith("." + domain)}