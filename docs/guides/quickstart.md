# 5 分钟快速上手

> 目标读者：刚接触爬虫，想要一个"拿来就能用"的资源调度工具。

本指南不预设你了解资源池、线程安全、异步编程——跟着走就能跑起来。

---

## 1. 安装

```bash
pip install git+https://github.com/nianchen8/resource-pool.git
```

Python ≥ 3.10 即可，只有一个硬依赖（`dnspython`）。

---

## 2. 第一个 User-Agent 轮换

固定 UA 是爬虫第一课被反的原因。三行代码轮换：

```python
from user_agent_pool import UserAgentPool

ua = UserAgentPool()
print(ua.get())          # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/..."
print(ua.get("mobile"))  # 限定移动端
```

每次 `get()` 返回不同 UA，自动加权随机——常用 UA 命中率更高。

---

## 3. 第一个 DNS 解析

单点 DNS 频次过高会被限流，14 台轮换：

```python
from dns_resolver_pool import DNSResolverPool

dns = DNSResolverPool()
dns.health_check()                    # 启动前检测一次
ip = dns.resolve("www.example.com")   # 选取延迟最低的 DNS 解析
```

解析结果自动缓存 5 分钟，同样的域名不会重复查询。

---

## 4. 第一个代理

```python
from proxy_pool import ProxyPool

proxy = ProxyPool()
proxy.add_proxy({"scheme": "http", "host": "127.0.0.1", "port": 8080})
proxy.health_check()  # 探测代理连通性

url = proxy.get()     # "http://127.0.0.1:8080"
```

故障代理会自动隔离，到期后会试用复活。

---

## 5. 三件事一起做

```python
from resource_pool import PoolOrchestrator, UserAgentPool, DNSResolverPool, ProxyPool

ua = UserAgentPool()
dns = DNSResolverPool()
dns.health_check()
proxy = ProxyPool()
proxy.add_proxy({"scheme": "http", "host": "127.0.0.1", "port": 8080})

orch = PoolOrchestrator(ua=ua, dns=dns, proxy=proxy)
combo = orch.next()  # 一次拿到全套

# 拿着去发请求
import requests
requests.get(
    "https://httpbin.org/ip",
    headers=combo["ua"],
    proxies=combo["proxy"],
)
```

---

## 6. 有现成的代理 API？一行加载

```python
proxy.load_from_url("http://你的代理供应商.com/api?key=xxx&count=20")
# → 自动识别 9 种主流供应商格式
```

---

## 接下来看什么？

| 你想做…… | 去看 |
|---------|------|
| 反反爬——完整请求头伪装 | [cookbook → UA 池](cookbook.md#user-agent-池) |
| Scrapy 项目接进来 | [cookbook → Scrapy 集成](cookbook.md#scrapy-集成) |
| 理解底层怎么设计的 | [深入架构](deep-dive.md) |
| 生产环境部署 | [PRODUCTION.md](../PRODUCTION.md) |
