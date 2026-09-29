from .base import BaseScanner
from app.core.config import settings

class SubfinderScanner(BaseScanner):
    name = "subfinder"
    async def run(self, domain: str) -> set[str]:
        raw = await self._exec([settings.gobin("subfinder"), "-d", domain, "-all", "-silent"])
        return self._clean(raw)