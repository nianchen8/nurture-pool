"""最小异步 create_resolver 验证"""
import asyncio
import aiohttp
from dns_resolver_pool.pool_async import AsyncDNSResolverPool

async def main():
    dns = AsyncDNSResolverPool()
    print(f"DNS: {dns}")

    resolver = dns.create_resolver()
    assert hasattr(resolver, "resolve"), "缺少 .resolve() 方法"

    connector = aiohttp.TCPConnector(resolver=resolver)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get("https://www.baidu.com",
                               timeout=aiohttp.ClientTimeout(total=15)) as resp:
            text = await resp.text()
            print(f"状态: {resp.status}, 长度: {len(text)}")
            assert resp.status == 200

    print("✅ create_resolver() 验证通过")

asyncio.run(main())
