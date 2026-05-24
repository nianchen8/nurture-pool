class PoolExhaustedException(Exception):
    """池中所有资源均已不可用"""

    def __init__(self, resource_type: str = "", detail: str = ""):
        msg = f"所有 {resource_type} 均不可用" if resource_type else "资源池已耗尽"
        if detail:
            msg += f"：{detail}"
        super().__init__(msg)


class ResourceUnhealthyException(Exception):
    """单个资源健康检查失败"""

    def __init__(self, resource_id: str, detail: str = ""):
        msg = f"资源 {resource_id} 健康检查失败"
        if detail:
            msg += f"：{detail}"
        super().__init__(msg)
