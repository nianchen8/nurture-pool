"""Resource Pool —— 可扩展的网络资源池框架

开箱即用的爬虫资源调度：User-Agent 池（含 Header Profile 组） + DNS 解析器池。

基本用法::

    from resource_pool import UserAgentPool, DNSResolverPool, SelectStrategy

    # UA 池
    ua_pool = UserAgentPool()
    ua = ua_pool.get("desktop")
    headers = ua_pool.get_headers("mobile")     # 完整 Header Profile

    # DNS 池
    dns_pool = DNSResolverPool(strategy=SelectStrategy.LATENCY_WEIGHTED)
    dns_pool.health_check()
    ip = dns_pool.resolve("www.example.com")

    # 统一捕获异常
    from resource_pool import PoolExhaustedError
    try:
        ip = dns_pool.resolve("blocked.example.com")
    except PoolExhaustedError:
        print("所有 DNS 都失败了")
"""

from resource_pool.exceptions import PoolExhaustedError, ResourceUnhealthyError

# ── 惰性导入 —— 避免按需使用时加载不必要的子包 ──────────────────────

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # attr_name → (module, qualname)
    "UserAgentPool":              ("user_agent_pool", "UserAgentPool"),
    "UAReserve":                  ("user_agent_pool", "UAReserve"),
    "VALID_CATEGORIES":           ("user_agent_pool", "VALID_CATEGORIES"),
    "AVAILABLE_PROFILES":         ("user_agent_pool", "AVAILABLE_PROFILES"),
    "UAPoolExhaustedException":   ("user_agent_pool.exceptions", "PoolExhaustedException"),
    "InvalidAgentException":      ("user_agent_pool.exceptions", "InvalidAgentException"),
    "DNSResolverPool":            ("dns_resolver_pool", "DNSResolverPool"),
    "SelectStrategy":             ("dns_resolver_pool", "SelectStrategy"),
    "DNSPoolExhaustedException":  ("dns_resolver_pool.exceptions", "PoolExhaustedException"),
    "ResourceUnhealthyException": ("dns_resolver_pool.exceptions", "ResourceUnhealthyException"),
    "PoolExhaustedError":         ("resource_pool.exceptions", "PoolExhaustedError"),
    "ResourceUnhealthyError":     ("resource_pool.exceptions", "ResourceUnhealthyError"),
    "ResourcePool":               ("resource_pool.base", "ResourcePool"),
    "SelectionStrategy":          ("resource_pool.base", "SelectionStrategy"),
}


def __getattr__(name: str) -> object:
    if name in _LAZY_IMPORTS:
        module_path, attr = _LAZY_IMPORTS[name]
        import importlib
        mod = importlib.import_module(module_path)
        value = getattr(mod, attr)
        # 缓存到模块全局，避免重复 import
        globals()[name] = value
        return value
    raise AttributeError(f"module 'resource_pool' has no attribute '{name}'")


__all__ = [
    # 公共异常
    "PoolExhaustedError",
    "ResourceUnhealthyError",
    # 抽象基类
    "ResourcePool",
    "SelectionStrategy",
    # UA 池
    "UserAgentPool",
    "UAReserve",
    "VALID_CATEGORIES",
    "AVAILABLE_PROFILES",
    "UAPoolExhaustedException",
    "InvalidAgentException",
    # DNS 池
    "DNSResolverPool",
    "SelectStrategy",
    "DNSPoolExhaustedException",
    "ResourceUnhealthyException",
]
