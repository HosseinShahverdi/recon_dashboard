import asyncio
import secrets
import dns.resolver

class WildcardGuard:
    async def detect(self, domain: str, samples: int = 5) -> set[str]:
        ips = set()
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3
        resolver.lifetime = 3

        def _resolve(nonce: str) -> set[str]:
            try: return {r.address for r in resolver.resolve(nonce, "A")}
            except Exception: return set()

        nonces = [f"nonce-{secrets.token_hex(6)}.{domain}" for _ in range(samples)]
        for n in nonces:
            ips |= await asyncio.to_thread(_resolve, n)
        return ips