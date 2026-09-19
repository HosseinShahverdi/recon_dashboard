from .base import BaseScanner

class AssetfinderScanner(BaseScanner):
    name = "assetfinder"

    async def run(self, domain: str) -> set[str]:
        raw = await self._exec(["assetfinder", "--subs-only", domain])
        return self._clean(raw)