"""资源池抽象基类 —— 定义统一接口协议"""

from abc import ABC, abstractmethod
from typing import Any, Iterator
import threading


class ResourcePool(ABC):
    """所有资源池的抽象基类

    子类需实现 __len__ 和 __repr__，可选实现 __contains__。
    框架层可依赖此基类做统一调度（如：遍历所有池做健康检查）。
    """

    _lock: threading.Lock

    @abstractmethod
    def __len__(self) -> int:
        """返回可用资源数量"""
        ...

    @abstractmethod
    def __repr__(self) -> str:
        """可读的运行时状态"""
        ...

    def __contains__(self, item: Any) -> bool:
        """是否包含指定资源（子类可按需覆盖）"""
        return False


class SelectionStrategy(ABC):
    """DNS 选择策略协议 —— 实现此协议的 callable 对象可作为自定义策略

    使用示例::

        class MyStrategy:
            def __call__(self, servers: list) -> Iterator:
                # 自定义排序/过滤逻辑
                return iter(sorted(servers, key=lambda s: s.weight, reverse=True))

        pool.strategy = MyStrategy()
    """

    @abstractmethod
    def __call__(self, servers: list) -> Iterator:
        """接收 alive 服务器列表，返回迭代器"""
        ...
