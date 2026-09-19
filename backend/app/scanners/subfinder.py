from .base import BaseScanner

class SubfinderScanner(BaseScanner):
    name = "subfinder"
    
    async def run(self, domain:str) -> set[str]:
        raw = await self._exec(["subfinder", "-d", domain, "-all", "-silent"])
        return self._clean(raw)
