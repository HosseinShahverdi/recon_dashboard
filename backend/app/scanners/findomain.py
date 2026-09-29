from .base import BaseScanner
from app.core.config import settings

class FindomainScanner(BaseScanner):
    name = "findomain"
    async def run(self, domain: str) -> set[str]:
        raw = await self._exec([settings.gobin("findomain"), "-t", domain, "-q"])
        return self._clean(raw)