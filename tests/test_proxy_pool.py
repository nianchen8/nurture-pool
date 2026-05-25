"""代理池测试"""

import pytest
from proxy_pool import ProxyPool, ProxyStrategy
from proxy_pool.exceptions import PoolExhaustedException


class TestProxyPool:
    """ProxyPool 基本操作"""

    def test_init_empty(self):
        pool = ProxyPool()
        assert len(pool) == 0
        assert "ProxyPool" in repr(pool)

    def test_add_proxy(self):
        pool = ProxyPool()
        pool.add_proxy({"scheme": "http", "host": "127.0.0.1", "port": 8080})
        assert len(pool) == 1

    def test_add_proxy_default_scheme(self):
        pool = ProxyPool()
        pool.add_proxy({"host": "10.0.0.1", "port": 3128})
        assert "http://10.0.0.1:3128" in pool

    def test_add_proxy_with_auth(self):
        pool = ProxyPool()
        pool.add_proxy({
            "scheme": "https",
            "host": "proxy.example.com",
            "port": 443,
            "username": "user1",
            "password": "pass1",
        })
        assert len(pool) == 1

    def test_add_duplicate_updates(self):
        pool = ProxyPool()
        pool.add_proxy({"scheme": "http", "host": "127.0.0.1", "port": 8080, "weight": 3})
        pool.add_proxy({"scheme": "http", "host": "127.0.0.1", "port": 8080, "weight": 8})
        assert len(pool) == 1

    def test_add_invalid_scheme(self):
        pool = ProxyPool()
        with pytest.raises(ValueError, match="无效 scheme"):
            pool.add_proxy({"scheme": "ftp", "host": "x", "port": 21})

    def test_add_missing_fields(self):
        pool = ProxyPool()
        with pytest.raises(ValueError, match="必须包含 host 和 port"):
            pool.add_proxy({"scheme": "http", "host": "x"})

    def test_remove_proxy(self):
        pool = ProxyPool()
        pool.add_proxy({"host": "127.0.0.1", "port": 8080})
        assert pool.remove_proxy("127.0.0.1", 8080) is True
        assert len(pool) == 0

    def test_remove_nonexistent(self):
        pool = ProxyPool()
        assert pool.remove_proxy("1.2.3.4", 80) is False

    def test_enable_proxy(self):
        pool = ProxyPool()
        pool.add_proxy({"host": "127.0.0.1", "port": 8080})
        pool.remove_proxy("127.0.0.1", 8080)
        assert pool.enable_proxy("127.0.0.1", 8080) is True
        assert len(pool) == 1

    def test_get_raises_when_empty(self):
        pool = ProxyPool()
        with pytest.raises(PoolExhaustedException, match="无可用代理"):
            pool.get()

    def test_get_returns_url(self):
        pool = ProxyPool()
        pool.add_proxy({"scheme": "http", "host": "10.0.0.1", "port": 8080})
        url = pool.get()
        assert url == "http://10.0.0.1:8080"

    def test_get_with_auth(self):
        pool = ProxyPool()
        pool.add_proxy({
            "scheme": "socks5", "host": "p.example.com", "port": 1080,
            "username": "u", "password": "p",
        })
        url = pool.get()
        assert url == "socks5://u:p@p.example.com:1080"

    def test_get_scheme_filter(self):
        pool = ProxyPool()
        pool.add_proxy({"scheme": "http", "host": "10.0.0.1", "port": 8080})
        pool.add_proxy({"scheme": "socks5", "host": "10.0.0.2", "port": 1080})
        url = pool.get(scheme="socks5")
        assert "socks5" in url
        assert "10.0.0.2" in url

    def test_get_dict(self):
        pool = ProxyPool()
        pool.add_proxy({"host": "10.0.0.1", "port": 8080})
        d = pool.get_dict()
        assert d == {"http": "http://10.0.0.1:8080", "https": "http://10.0.0.1:8080"}

    def test_stats(self):
        pool = ProxyPool()
        pool.add_proxy({"host": "a.com", "port": 80, "region": "us"})
        stats = pool.stats()
        assert len(stats) == 1
        assert stats[0]["proxy"] == "http://a.com:80"
        assert stats[0]["region"] == "us"

    def test_strategy_property(self):
        pool = ProxyPool(strategy=ProxyStrategy.RANDOM)
        assert pool.strategy == ProxyStrategy.RANDOM
        pool.strategy = ProxyStrategy.ROUND_ROBIN
        assert pool.strategy == ProxyStrategy.ROUND_ROBIN

    def test_repr(self):
        pool = ProxyPool()
        pool.add_proxy({"host": "a.com", "port": 80})
        r = repr(pool)
        assert "alive=1/1" in r
        assert "latency_weighted" in r

    def test_len_alive_only(self):
        pool = ProxyPool()
        pool.add_proxy({"host": "a.com", "port": 80})
        pool.add_proxy({"host": "b.com", "port": 80})
        assert len(pool) == 2
        pool.remove_proxy("a.com", 80)
        assert len(pool) == 1

    def test_contains(self):
        pool = ProxyPool()
        pool.add_proxy({"host": "10.0.0.1", "port": 8080})
        assert "http://10.0.0.1:8080" in pool
        assert "http://9.9.9.9:8080" not in pool


class TestProxyStrategy:
    """策略测试"""

    def test_round_robin_cycles(self):
        pool = ProxyPool(strategy=ProxyStrategy.ROUND_ROBIN)
        pool.add_proxy({"host": "10.0.0.1", "port": 8080})
        pool.add_proxy({"host": "10.0.0.2", "port": 8080})
        pool.add_proxy({"host": "10.0.0.3", "port": 8080})

        urls = {pool.get() for _ in range(3)}
        assert len(urls) >= 2  # 至少轮到了2个不同的

    def test_random_distribution(self):
        pool = ProxyPool(strategy=ProxyStrategy.RANDOM)
        for i in range(5):
            pool.add_proxy({"host": f"10.0.0.{i}", "port": 8080})

        urls = {pool.get() for _ in range(20)}
        assert len(urls) >= 2  # 至少选中2个不同的

    def test_latency_weighted_prefers_fast(self):
        """添加两台代理，手动设置一台延迟更低，应被优先选中"""
        pool = ProxyPool(strategy=ProxyStrategy.LATENCY_WEIGHTED)
        pool.add_proxy({"host": "fast.proxy", "port": 80, "weight": 10})
        pool.add_proxy({"host": "slow.proxy", "port": 80, "weight": 10})

        # 手动设置延迟
        for s in pool._proxies:
            if s.host == "fast.proxy":
                s.latency_ms = 10.0
            else:
                s.latency_ms = 500.0

        # 延迟加权每次应选中最快的
        chosen = [pool.get() for _ in range(20)]
        fast_count = sum(1 for u in chosen if "fast.proxy" in u)
        assert fast_count == 20, f"延迟加权应总选最快，实际选中 fast {fast_count}/20"

    def test_custom_callable_strategy(self):
        """自定义 callable 策略"""
        pool = ProxyPool()
        pool.add_proxy({"host": "a.com", "port": 80, "weight": 1})
        pool.add_proxy({"host": "b.com", "port": 80, "weight": 100})

        def highest_weight(proxies):
            best = max(proxies, key=lambda s: s.weight)
            return iter([best])

        pool.strategy = highest_weight
        for _ in range(10):
            assert "b.com" in pool.get()


class TestFaultIsolation:
    """故障隔离"""

    def test_isolated_not_returned(self):
        pool = ProxyPool()
        pool.add_proxy({"host": "good.proxy", "port": 80})
        pool.add_proxy({"host": "bad.proxy", "port": 80})

        # 模拟故障隔离
        for s in pool._proxies:
            if s.host == "bad.proxy":
                s.enabled = False

        urls = {pool.get() for _ in range(10)}
        assert all("good.proxy" in u for u in urls)

    def test_revive_after_timeout(self):
        pool = ProxyPool(revive_after=0)
        pool.add_proxy({"host": "revive.proxy", "port": 80})

        for s in pool._proxies:
            s.enabled = False
            s.last_health = 0  # 很久以前

        # 第一次调用触发复活（_try_revive 在 _pick_one 内部执行），
        # 复活后将 enabled 置 True；第二次调用即可取到
        pool._last_revive_check = 0
        try:
            pool.get()  # 第一次：触发复活但 alive 已空
        except Exception:
            pass
        url = pool.get()  # 第二次：复活后可用
        assert "revive.proxy" in url


class TestThreadSafeOff:
    """thread_safe=False 模式"""

    def test_get_works(self):
        pool = ProxyPool(thread_safe=False)
        pool.add_proxy({"host": "10.0.0.1", "port": 8080})
        url = pool.get()
        assert url == "http://10.0.0.1:8080"

    def test_stats_works(self):
        pool = ProxyPool(thread_safe=False)
        pool.add_proxy({"host": "a.com", "port": 80})
        stats = pool.stats()
        assert len(stats) == 1
