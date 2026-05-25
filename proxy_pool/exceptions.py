"""代理池异常"""

from resource_pool.exceptions import PoolExhaustedError


class PoolExhaustedException(PoolExhaustedError):
    """代理池中所有资源均不可用时抛出"""

    def __init__(self, detail: str = ""):
        msg = "所有代理均不可用"
        if detail:
            msg += f"：{detail}"
        super().__init__(msg)


class ProxyUnhealthyException(Exception):
    """单个代理健康检查失败"""

    def __init__(self, proxy: str, detail: str = ""):
        msg = f"代理 {proxy} 健康检查失败"
        if detail:
            msg += f"：{detail}"
        super().__init__(msg)
