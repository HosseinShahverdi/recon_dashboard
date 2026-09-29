import asyncio
from pathlib import Path
from .base import BaseScanner
from app.core.config import settings

class ShufflednsScanner(BaseScanner):
    name = "shuffledns"
    def __init__(self, timeout: int = 900):
        super().__init__(timeout)

    async def run(self, domain: str) -> set[str]:
        wordlist = settings.WORDLIST_DIR / "subdomains-top5k.txt"
        resolvers = settings.WORDLIST_DIR / "resolvers.txt"
        outfile = Path(f"/tmp/shuffledns_{domain}.txt")

        cmd = [
            settings.gobin("shuffledns"), "-d", domain,
            "-w", str(wordlist), "-r", str(resolvers),
            "-m", settings.gobin("massdns"),
            "-mode", "bruteforce", "-silent", "-o", str(outfile),
        ]
        await self._exec(cmd)

        if outfile.exists():
            raw = outfile.read_text(errors="ignore")
            outfile.unlink(missing_ok=True)
            return self._clean(raw)
        return set()