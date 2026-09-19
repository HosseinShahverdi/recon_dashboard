from .base import BaseScanner

class FindomainScanner(BaseScanner):
    name = "findomain"

    async def run(self, domain: str) -> set[str]:
        raw = await self._exec(["findomain", "-t", domain, "-q"])
        return self._clean(raw)