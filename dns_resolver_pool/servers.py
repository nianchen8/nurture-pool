"""内置 DNS 服务器注册表 —— 可作为蓝本自行扩展"""

from typing import TypedDict


class ServerEntry(TypedDict, total=False):
    ip: str
    name: str
    region: str
    enabled: bool
    weight: int


# ── 国内高速 DNS ────────────────────────────────────────────────────
_DOMESTIC: list[ServerEntry] = [
    {"ip": "114.114.114.114", "name": "114DNS", "region": "domestic", "enabled": True, "weight": 10},
    {"ip": "223.5.5.5",       "name": "阿里 DNS", "region": "domestic", "enabled": True, "weight": 10},
    {"ip": "223.6.6.6",       "name": "阿里 DNS 备用", "region": "domestic", "enabled": True, "weight": 8},
    {"ip": "119.29.29.29",    "name": "DNSPod", "region": "domestic", "enabled": True, "weight": 9},
    {"ip": "180.76.76.76",    "name": "百度 DNS", "region": "domestic", "enabled": True, "weight": 7},
    {"ip": "101.226.4.6",     "name": "DNS派 电信", "region": "domestic", "enabled": True, "weight": 6},
    {"ip": "218.30.118.6",    "name": "DNS派 联通", "region": "domestic", "enabled": True, "weight": 6},
]

# ── 海外 DNS ────────────────────────────────────────────────────────
_OVERSEAS: list[ServerEntry] = [
    {"ip": "8.8.8.8",        "name": "Google DNS", "region": "overseas", "enabled": True, "weight": 8},
    {"ip": "8.8.4.4",        "name": "Google DNS 备用", "region": "overseas", "enabled": True, "weight": 7},
    {"ip": "1.1.1.1",        "name": "Cloudflare", "region": "overseas", "enabled": True, "weight": 10},
    {"ip": "1.0.0.1",        "name": "Cloudflare 备用", "region": "overseas", "enabled": True, "weight": 8},
    {"ip": "9.9.9.9",        "name": "Quad9", "region": "overseas", "enabled": True, "weight": 6},
    {"ip": "208.67.222.222", "name": "OpenDNS", "region": "overseas", "enabled": True, "weight": 6},
    {"ip": "208.67.220.220", "name": "OpenDNS 备用", "region": "overseas", "enabled": True, "weight": 5},
]

# ── 健康检查探测域名 ─────────────────────────────────────────────────
HEALTH_CHECK_DOMAINS = [
    "www.baidu.com",
    "dns.google",
    "one.one.one.one",
    "resolver1.opendns.com",
]
