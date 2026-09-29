import asyncio
import json
from app.core.config import settings

class DnsxResolver:
    async def resolve(self, hosts: list[str]) -> dict[str, dict]:
        if not hosts: return {}
        proc = await asyncio.create_subprocess_exec(
            settings.gobin("dnsx"), "-silent", "-json", "-a", "-cname",
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate(input="\n".join(hosts).encode())
        out = {}
        for line in stdout.decode(errors="ignore").splitlines():
            if not line.strip().startswith("{"): continue
            try: data = json.loads(line)
            except json.JSONDecodeError: continue
            host = (data.get("host") or "").lower()
            if not host: continue
            a = data.get("a") or []
            cname = data.get("cname")
            out[host] = {
                "ip": a[0] if isinstance(a, list) and a else None,
                "cname": cname[0] if isinstance(cname, list) else cname,
            }
        return out