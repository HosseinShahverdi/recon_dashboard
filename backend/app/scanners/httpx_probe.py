import asyncio
import json

# Run `httpx -h` yourself to explore every flag — this is our enrichment recipe
HTTPX_FLAGS = [
    "-silent", "-json", "-status-code", "-content-length", "-title",
    "-web-server", "-tech-detect", "-ip", "-cname", "-asn",
    "-follow-redirects", "-timeout", "10", "-threads", "40",
]

CDN_MARKERS = ["cloudflare", "akamai", "fastly", "cloudfront", "azure",
               "incapsula", "imperva", "sucuri"]


def _first(value):
    """httpx returns lists for -ip/-cname; we want the first entry or None."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _detect_cdn(info: dict) -> str | None:
    blob = " ".join(filter(None, [info.get("webserver"), info.get("cname"),
                                  info.get("asn")])).lower()
    for marker in CDN_MARKERS:
        if marker in blob:
            return marker
    return None


class HttpxProbe:
    """Feeds subdomains into httpx via stdin, parses the JSONL stream."""

    async def probe(self, subdomains: list[str]) -> dict[str, dict]:
        if not subdomains:
            return {}

        proc = await asyncio.create_subprocess_exec(
            "httpx", *HTTPX_FLAGS,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate(input="\n".join(subdomains).encode())

        results: dict[str, dict] = {}
        for line in stdout.decode(errors="ignore").splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                data = json.loads(line)          # TEACH POINT: defensive parsing
            except json.JSONDecodeError:
                continue

            url = data.get("url", "")
            if "://" not in url:
                continue
            scheme, rest = url.split("://", 1)
            host = rest.split("/")[0].split(":")[0].lower()

            info = {
                "status_code": data.get("status_code"),
                "scheme": scheme,
                "ip": _first(data.get("a") or data.get("ip")),
                "asn": data.get("asn") if isinstance(data.get("asn"), str) else None,
                "port": data.get("port"),
                "length": data.get("content_length"),
                "cname": _first(data.get("cname")),
                "title": data.get("title"),
                "webserver": data.get("webserver"),
                "tech_stack": data.get("tech") or [],
            }
            info["cdn"] = _detect_cdn(info)
            results[host] = info
        return results