"""User-Agent 资源池

提供线程安全的 User-Agent 管理，支持按设备分类（desktop/mobile/tablet）的加权/均匀随机获取。

基本用法::

    from user_agent_pool import UserAgentPool

    pool = UserAgentPool()
    ua = pool.get("mobile")                     # 加权随机
    print(pool.count())                         # {'desktop': 10, ...}

    with pool.reserve("desktop") as ua:
        # 用完自动回收
        pass
"""

from user_agent_pool.pool import UserAgentPool, UAReserve
from user_agent_pool.exceptions import PoolExhaustedError, InvalidAgentError
from user_agent_pool.agents import VALID_CATEGORIES

__all__ = [
    "UserAgentPool",
    "UAReserve",
    "PoolExhaustedError",
    "InvalidAgentError",
    "VALID_CATEGORIES",
]
