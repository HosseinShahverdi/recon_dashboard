import asyncio
from abc import ABC, abstractmethod


class BaseScanner(ABC):
    """Every scanner, no matter the tool, returns a set of subdomain strings."""

    name: str = "base"

    def __init__(self, timeout: int = 300):
        self.timeout = timeout

    @abstractmethod
    async def run(self, domain: str) -> set[str]:
        ...

    async def _exec(self, cmd: list[str]) -> str:
        """
        TEACH POINT: asyncio.create_subprocess_exec runs the binary in a child
        process WITHOUT blocking FastAPI's event loop. The API stays responsive
        while subfinder works.
        """
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=self.timeout)
        except asyncio.TimeoutError:
            proc.kill()          # never let a hung tool kill the scan
            return ""
        return stdout.decode(errors="ignore")

    @staticmethod
    def _clean(raw: str) -> set[str]:
        """Normalize tool output: lowercase, strip wildcards/garbage."""
        out = set()
        for line in raw.splitlines():
            line = line.strip().lower().rstrip(".")
            if line and "*" not in line and " " not in line:
                out.add(line)
        return out