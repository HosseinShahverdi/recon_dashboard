from .base import BaseScanner
from app.core.config import settings

class AssetfinderScanner(BaseScanner):
    name = "assetfinder"
    async def run(self, domain: str) -> set[str]:
        raw = await self._exec([settings.gobin("assetfinder"), "--subs-only", domain])
        return self._clean(raw)