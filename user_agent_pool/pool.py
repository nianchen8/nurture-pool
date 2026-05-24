"""User-Agent 资源池核心逻辑"""

import random
import threading
from typing import Iterator

from user_agent_pool.exceptions import PoolExhaustedError, InvalidAgentError
from user_agent_pool.agents import (
    DEFAULT_AGENTS,
    VALID_CATEGORIES,
    AgentEntry,
)


class UserAgentPool:
    """线程安全的 User-Agent 资源池

    支持：
    - 按分类获取：desktop / mobile / tablet / all
    - 加权随机 / 均匀随机
    - 动态增删
    - 上下文管理器（暂存池，用完自动回收）

    使用示例::

        pool = UserAgentPool()
        ua = pool.get()                    # 随机获取一个（all 分类）
        ua = pool.get("mobile")           # 只拿 mobile
        ua = pool.get("desktop", weighted=False)  # 均匀随机

        with pool.reserve("mobile") as ua:
            # 做请求...
            pass
    """

    def __init__(self) -> None:
        self._agents: dict[str, list[AgentEntry]] = {}
        self._init_defaults()
        self._lock = threading.Lock()

    # ── 初始化 ───────────────────────────────────────────────────────

    def _init_defaults(self) -> None:
        """从 agents.py 导入内置数据集"""
        for cat in ("desktop", "mobile", "tablet"):
            self._agents[cat] = [entry.copy() for entry in DEFAULT_AGENTS[cat]]

    # ── 公开 API ─────────────────────────────────────────────────────

    def get(self, category: str = "all", weighted: bool = True) -> str:
        """从池中获取一个 User-Agent 字符串

        Args:
            category: desktop | mobile | tablet | all
            weighted: True=按权重加权随机；False=均匀随机

        Returns:
            User-Agent 字符串

        Raises:
            PoolExhaustedError: 该分类下无可用 UA
        """
        candidates = self._pick_candidates(category)
        if not candidates:
            raise PoolExhaustedError(category)

        if weighted:
            return self._weighted_choice(candidates)
        return random.choice(candidates)["ua"]

    def get_all(self, category: str = "all") -> list[str]:
        """获取该分类下所有 UA 字符串（不修改池）"""
        return [entry["ua"] for entry in self._pick_candidates(category)]

    def add(self, ua: str, category: str, weight: int = 5) -> None:
        """向指定分类添加一个 UA

        Raises:
            ValueError: 分类不合法
            InvalidAgentError: ua 为空
        """
        if category not in VALID_CATEGORIES or category == "all":
            raise ValueError(f"无效分类 '{category}'，可选: {VALID_CATEGORIES}")
        if not ua or not ua.strip():
            raise InvalidAgentError("UA 不能为空")

        entry: AgentEntry = {"ua": ua.strip(), "weight": max(1, weight)}
        with self._lock:
            self._agents.setdefault(category, []).append(entry)

    def remove(self, ua: str, category: str | None = None) -> int:
        """移除匹配的 UA，返回移除数量

        若未指定 category，则遍历所有分类。
        """
        removed = 0
        cats = [category] if category else list(self._agents.keys())
        with self._lock:
            for cat in cats:
                if cat not in self._agents:
                    continue
                before = len(self._agents[cat])
                self._agents[cat] = [
                    e for e in self._agents[cat] if e["ua"] != ua
                ]
                removed += before - len(self._agents[cat])
        return removed

    def count(self, category: str | None = None) -> dict[str, int]:
        """统计各分类 UA 数量"""
        cats = [category] if category else list(self._agents.keys())
        return {c: len(self._agents.get(c, [])) for c in cats}

    def reserve(self, category: str = "all", weighted: bool = True) -> "UAReserve":
        """上下文管理器 —— 取出一个 UA，退出时自动回收

        使用::

            with pool.reserve("mobile") as ua:
                requests.get(url, headers={"User-Agent": ua})
        """
        return UAReserve(self, category, weighted)

    # ── 内部方法 ─────────────────────────────────────────────────────

    def _pick_candidates(self, category: str) -> list[AgentEntry]:
        if category == "all":
            candidates: list[AgentEntry] = []
            with self._lock:
                for entries in self._agents.values():
                    candidates.extend(entries)
            return candidates
        with self._lock:
            return list(self._agents.get(category, []))

    @staticmethod
    def _weighted_choice(entries: list[AgentEntry]) -> str:
        """加权随机选择"""
        total = sum(e["weight"] for e in entries)
        if total == 0:
            return random.choice(entries)["ua"]
        r = random.uniform(0, total)
        cumulative = 0.0
        for entry in entries:
            cumulative += entry["weight"]
            if r <= cumulative:
                return entry["ua"]
        return entries[-1]["ua"]

    def __repr__(self) -> str:
        stats = ", ".join(f"{c}={len(v)}" for c, v in self._agents.items())
        return f"UserAgentPool({stats})"

    def __len__(self) -> int:
        return sum(len(v) for v in self._agents.values())

    def __iter__(self) -> Iterator[str]:
        """迭代所有类别的所有 UA"""
        for entries in self._agents.values():
            yield from (e["ua"] for e in entries)


class UAReserve:
    """UA 暂存器 —— 陪跑上下文管理器，退出时把 UA 归还池"""

    def __init__(self, pool: UserAgentPool, category: str, weighted: bool) -> None:
        self._pool = pool
        self._category = category
        self._weighted = weighted
        self.ua: str = ""

    def __enter__(self) -> str:
        self.ua = self._pool.get(self._category, self._weighted)
        return self.ua

    def __exit__(self, *args: object) -> None:
        """退出时自动 add 回池子"""
        if self.ua and self._category != "all":
            try:
                self._pool.add(self.ua, self._category)
            except (ValueError, InvalidAgentError):
                pass
