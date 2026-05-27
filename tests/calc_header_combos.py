"""计算"Identity Block + 可变字段"架构下的最大合法 Header 组合数

每个组合必须满足：
1. UA 版本 == Sec-Ch-Ua 版本                                    (_patch_sec_ch_ua 保证)
2. UA 平台 == Sec-Ch-Ua-Platform                                 (设计保证)
3. UA 设备类型 == Sec-Ch-Ua-Mobile                               (设计保证)
4. Accept-Language 段数 == 设备类型                               (desktop>=5, mobile<=3)
5. Sec-Ch-Ua 格式 == 版本范围                                    (3种格式)
6. 派系模板不可交叉                                              (Chrome↮Firefox↮Safari)
"""

# ═══════════════════════════════════════════════════════════════
# 1. Chrome/Chromium 派系
# ═══════════════════════════════════════════════════════════════

CHROME_VERSIONS = {
    "v129": {"sec_ch_ua_fmt": "A", "not_brand": 'Not=A?Brand;v="8"'},
    "v130": {"sec_ch_ua_fmt": "B", "not_brand": 'Not?A_Brand;v="99"'},
    "v131": {"sec_ch_ua_fmt": "C", "not_brand": 'Not_A Brand;v="24"'},
    "v132": {"sec_ch_ua_fmt": "C", "not_brand": 'Not_A Brand;v="24"'},
    "v133": {"sec_ch_ua_fmt": "C", "not_brand": 'Not_A Brand;v="24"'},
    "v134": {"sec_ch_ua_fmt": "C", "not_brand": 'Not_A Brand;v="24"'},
    "v135": {"sec_ch_ua_fmt": "C", "not_brand": 'Not_A Brand;v="24"'},
    "v136": {"sec_ch_ua_fmt": "C", "not_brand": 'Not_A Brand;v="24"'},
    "v137": {"sec_ch_ua_fmt": "C", "not_brand": 'Not_A Brand;v="24"'},
    "v138": {"sec_ch_ua_fmt": "C", "not_brand": 'Not_A Brand;v="24"'},
    "v139": {"sec_ch_ua_fmt": "C", "not_brand": 'Not_A Brand;v="24"'},
    "v140": {"sec_ch_ua_fmt": "D", "not_brand": 'Not_A Brand;v="99"'},
    "v141": {"sec_ch_ua_fmt": "D", "not_brand": 'Not_A Brand;v="99"'},
    "v142": {"sec_ch_ua_fmt": "D", "not_brand": 'Not_A Brand;v="99"'},
    "v143": {"sec_ch_ua_fmt": "D", "not_brand": 'Not_A Brand;v="99"'},
    "v144": {"sec_ch_ua_fmt": "D", "not_brand": 'Not_A Brand;v="99"'},
    "v145": {"sec_ch_ua_fmt": "D", "not_brand": 'Not_A Brand;v="99"'},
    "v146": {"sec_ch_ua_fmt": "D", "not_brand": 'Not_A Brand;v="99"'},
    "v147": {"sec_ch_ua_fmt": "D", "not_brand": 'Not_A Brand;v="99"'},
    "v148": {"sec_ch_ua_fmt": "D", "not_brand": 'Not_A Brand;v="99"'},
}

# Desktop 平台
CHROME_DESKTOP_OS = {
    "Windows NT 10.0; Win64; x64": {"sec_ch_ua_platform": '"Windows"', "sec_ch_ua_mobile": "?0"},
    "Windows NT 10.0; WOW64":      {"sec_ch_ua_platform": '"Windows"', "sec_ch_ua_mobile": "?0"},
    "Macintosh; Intel Mac OS X 10_15_7":  {"sec_ch_ua_platform": '"macOS"',   "sec_ch_ua_mobile": "?0"},
    "X11; Linux x86_64":           {"sec_ch_ua_platform": '"Linux"',   "sec_ch_ua_mobile": "?0"},
}

# Mobile 平台 (Android, 不同设备型号)
CHROME_MOBILE_DEVICES = {
    "Linux; Android 15; Pixel 9 Pro":         "Pixel 9 Pro",
    "Linux; Android 14; Pixel 8 Pro":         "Pixel 8 Pro",
    "Linux; Android 14; SM-S928B":            "Galaxy S24 Ultra",
    "Linux; Android 13; Pixel 7":             "Pixel 7",
    "Linux; Android 14; 23127PN0CC":          "Xiaomi 14",
    "Linux; Android 13; ALN-AL80":            "Huawei Mate 60",
}

# Tablet 平台
CHROME_TABLET_DEVICES = {
    "Linux; Android 15; SM-X920":             "Galaxy Tab S9",
    "Linux; Android 14; SM-X910":             "Galaxy Tab S8",
    "Linux; Android 13; AGS6-W00":            "Huawei MatePad",
}

# Desktop Accept-Language: 5 段（桌面特征）
AL_DESKTOP_5 = [
    "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,ja;q=0.6",
    "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ko;q=0.6",
    "en-US,en;q=0.9,es;q=0.8,fr;q=0.7,de;q=0.6",
    "ja;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,ko;q=0.5",
]

# macOS Accept-Language: 4 段
AL_MACOS = [
    "zh-CN,zh-Hans;q=0.9,en;q=0.8",
    "en-US,en;q=0.9,zh-Hans;q=0.8",
    "zh-Hant,zh;q=0.9,en-US;q=0.8",
]

# Mobile/Tablet Accept-Language: 3 段（移动特征）
AL_MOBILE_3 = [
    "zh-CN,zh;q=0.9,en-US;q=0.8",
    "en-US,en;q=0.9,zh-CN;q=0.8",
    "zh-CN,zh;q=0.9,en;q=0.7",
]

# Cache-Control 变体
CACHE_CONTROL = ["max-age=0", "no-cache"]

# Upgrade-Insecure-Requests
UPGRADE = [True, False]  # True=包含 "1", False=不包含

# Accept 变体（Chrome 桌面版）
ACCEPT_CHROME = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
]


def calc_chrome():
    """Chrome 派系 = Desktop + Mobile + Tablet"""
    total = 0
    details = {}

    # ── Desktop ──
    desktop = 0
    for os_name, os_meta in CHROME_DESKTOP_OS.items():
        is_macos = "Macintosh" in os_name
        al_opts = AL_MACOS if is_macos else AL_DESKTOP_5
        for ver_name, ver_meta in CHROME_VERSIONS.items():
            # UA 存在性检查：低版本 Android 设备不跑太新的 Chrome
            # Desktop 所有版本都合法
            for al in al_opts:
                for cc in CACHE_CONTROL:
                    for up in UPGRADE:
                        desktop += 1
    details["Chrome Desktop"] = {
        "platforms": len(CHROME_DESKTOP_OS),
        "versions": len(CHROME_VERSIONS),
        "AL_variants": f"{len(AL_DESKTOP_5)}(Win/Lin)+{len(AL_MACOS)}(macOS)",
        "Cache-Control": len(CACHE_CONTROL),
        "Upgrade": len(UPGRADE),
        "subtotal": desktop,
    }
    total += desktop

    # ── Mobile ──
    mobile = 0
    mobile_versions = {k: v for k, v in CHROME_VERSIONS.items() if int(k[1:]) >= 129}
    for dev, dev_name in CHROME_MOBILE_DEVICES.items():
        for ver_name in mobile_versions:
            for al in AL_MOBILE_3:
                for cc in CACHE_CONTROL:
                    for up in UPGRADE:
                        mobile += 1
    details["Chrome Mobile"] = {
        "devices": len(CHROME_MOBILE_DEVICES),
        "versions": len(mobile_versions),
        "AL_variants": len(AL_MOBILE_3),
        "Cache-Control": len(CACHE_CONTROL),
        "Upgrade": len(UPGRADE),
        "subtotal": mobile,
    }
    total += mobile

    # ── Tablet ──
    tablet = 0
    tablet_versions = {k: v for k, v in CHROME_VERSIONS.items() if int(k[1:]) >= 130}
    for dev, dev_name in CHROME_TABLET_DEVICES.items():
        for ver_name in tablet_versions:
            for al in AL_MOBILE_3:  # Tablet 也用 3 段
                for cc in CACHE_CONTROL:
                    for up in UPGRADE:
                        tablet += 1
    details["Chrome Tablet"] = {
        "devices": len(CHROME_TABLET_DEVICES),
        "versions": len(tablet_versions),
        "AL_variants": len(AL_MOBILE_3),
        "Cache-Control": len(CACHE_CONTROL),
        "Upgrade": len(UPGRADE),
        "subtotal": tablet,
    }
    total += tablet

    return total, details


# ═══════════════════════════════════════════════════════════════
# 2. Edge 派系（Chromium 内核，但独立模板）
# ═══════════════════════════════════════════════════════════════

EDGE_VERSIONS = {
    "v131": "Not_A Brand;v=\"24\"",
    "v143": "Not_A Brand;v=\"99\"",
    "v145": "Not_A Brand;v=\"99\"",
    "v147": "Not_A Brand;v=\"99\"",
    "v148": "Not_A Brand;v=\"99\"",
}

EDGE_OS = {
    "Windows NT 10.0; Win64; x64": {"platform": '"Windows"', "mobile": "?0"},
    "Windows NT 10.0; WOW64":      {"platform": '"Windows"', "mobile": "?0"},
    "Macintosh; Intel Mac OS X 10_15_7": {"platform": '"macOS"', "mobile": "?0"},
}


def calc_edge():
    total = 0
    for os_name, os_meta in EDGE_OS.items():
        is_macos = "Macintosh" in os_name
        al_opts = AL_MACOS if is_macos else AL_DESKTOP_5
        for ver_name in EDGE_VERSIONS:
            for al in al_opts:
                for cc in CACHE_CONTROL:
                    for up in UPGRADE:
                        total += 1
    return total, {
        "platforms": len(EDGE_OS),
        "versions": len(EDGE_VERSIONS),
        "AL_variants": f"{len(AL_DESKTOP_5)}(Win)+{len(AL_MACOS)}(macOS)",
        "Cache-Control": len(CACHE_CONTROL),
        "Upgrade": len(UPGRADE),
        "subtotal": total,
    }


# ═══════════════════════════════════════════════════════════════
# 3. Firefox 派系
# ═══════════════════════════════════════════════════════════════

FIREFOX_VERSIONS = list(range(132, 152))  # 132 ~ 151

FIREFOX_DESKTOP_OS = [
    "Windows NT 10.0; Win64; x64; rv:{v}.0",
    "Windows NT 10.0; WOW64; rv:{v}.0",
    "Macintosh; Intel Mac OS X 10.15; rv:{v}.0",
    "X11; Linux x86_64; rv:{v}.0",
]

FIREFOX_MOBILE = [
    "Android 14; Mobile; rv:{v}.0",
    "Android 15; Mobile; rv:{v}.0",
]

# Firefox Accept-Language
AL_FIREFOX = [
    "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "en-US,en;q=0.5,zh-CN;q=0.3",
    "zh-CN,zh;q=0.9,en;q=0.5",
]


def calc_firefox():
    total = 0
    details = {}

    # Desktop (Firefox 无 Cache-Control 头)
    desktop = 0
    for os_tpl in FIREFOX_DESKTOP_OS:
        for ver in FIREFOX_VERSIONS:
            for al in AL_FIREFOX:
                for up in UPGRADE:  # Firefox 有 Upgrade-Insecure-Requests
                    desktop += 1
    details["Firefox Desktop"] = {
        "platforms": len(FIREFOX_DESKTOP_OS),
        "versions": len(FIREFOX_VERSIONS),
        "AL_variants": len(AL_FIREFOX),
        "Upgrade": len(UPGRADE),
        "subtotal": desktop,
    }
    total += desktop

    # Mobile
    mobile = 0
    mobile_versions = [v for v in FIREFOX_VERSIONS if v >= 133]
    for dev_tpl in FIREFOX_MOBILE:
        for ver in mobile_versions:
            for al in AL_FIREFOX:
                mobile += 1
    details["Firefox Mobile"] = {
        "devices": len(FIREFOX_MOBILE),
        "versions": len(mobile_versions),
        "AL_variants": len(AL_FIREFOX),
        "subtotal": mobile,
    }
    total += mobile

    return total, details


# ═══════════════════════════════════════════════════════════════
# 4. Safari 派系
# ═══════════════════════════════════════════════════════════════

SAFARI = {
    "macOS 18.1": {
        "ua_os": "Macintosh; Intel Mac OS X 10_15_7",
        "webkit_ver": "605.1.15",
        "safari_ver": "18.1",
        "al": ["zh-CN,zh-Hans;q=0.9,en;q=0.8", "en-US,en;q=0.9,zh-Hans;q=0.8"],
    },
    "macOS 17.6": {
        "ua_os": "Macintosh; Intel Mac OS X 10_15_7",
        "webkit_ver": "605.1.15",
        "safari_ver": "17.6",
        "al": ["zh-CN,zh-Hans;q=0.9", "en-US,en;q=0.9"],
    },
    "iPhone 18.1": {
        "ua_device": "iPhone; CPU iPhone OS 18_1 like Mac OS X",
        "webkit_ver": "605.1.15",
        "safari_ver": "18.1",
        "al": ["zh-CN,zh-Hans;q=0.9", "en-US,en;q=0.9"],
    },
    "iPhone 17.6": {
        "ua_device": "iPhone; CPU iPhone OS 17_7 like Mac OS X",
        "webkit_ver": "605.1.15",
        "safari_ver": "17.6",
        "al": ["zh-CN,zh-Hans;q=0.9", "en-US,en;q=0.9"],
    },
    "iPad 18.1": {
        "ua_device": "iPad; CPU OS 18_1 like Mac OS X",
        "webkit_ver": "605.1.15",
        "safari_ver": "18.1",
        "al": ["zh-CN,zh-Hans;q=0.9", "en-US,en;q=0.9"],
    },
    "iPad 17.6": {
        "ua_device": "iPad; CPU OS 17_7 like Mac OS X",
        "webkit_ver": "605.1.15",
        "safari_ver": "17.6",
        "al": ["zh-CN,zh-Hans;q=0.9", "en-US,en;q=0.9"],
    },
}


def calc_safari():
    total = 0
    details = {}
    for name, cfg in SAFARI.items():
        combs = len(cfg["al"]) * len(CACHE_CONTROL)
        device_type = "Desktop" if "macOS" in name else ("Mobile" if "iPhone" in name else "Tablet")
        details[name] = {
            "type": device_type,
            "AL_variants": len(cfg["al"]),
            "Cache-Control": len(CACHE_CONTROL),
            "subtotal": combs,
        }
        total += combs
    return total, details


# ═══════════════════════════════════════════════════════════════
# 汇总
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    chrome_total, chrome_details = calc_chrome()
    edge_total, edge_details = calc_edge()
    firefox_total, firefox_details = calc_firefox()
    safari_total, safari_details = calc_safari()

    print("=" * 72)
    print("  Header 合法组合数 —— 派系化 Identity Block + 可变字段")
    print("=" * 72)

    grand_total = 0

    print("\n── Chrome/Chromium 派系 ──")
    for name, d in chrome_details.items():
        print(f"  {name:20s}  {d['subtotal']:>6,d}  组合")
        grand_total += d["subtotal"]

    print("\n  ── Edge ──")
    print(f"  {'Edge Desktop':20s}  {edge_details['subtotal']:>6,d}  组合")
    grand_total += edge_total

    print("\n── Firefox 派系 ──")
    for name, d in firefox_details.items():
        print(f"  {name:20s}  {d['subtotal']:>6,d}  组合")
        grand_total += d["subtotal"]

    print("\n── Safari 派系 ──")
    for name, d in safari_details.items():
        print(f"  {name:20s}  {d['subtotal']:>6,d}  组合")
        grand_total += d["subtotal"]

    print(f"\n{'─' * 72}")
    print(f"  ★ 总计合法组合: {grand_total:,}")
    print("     (当前固定列表: 31 条)")
    print(f"     膨胀倍数: {grand_total / 31:.1f}×")
    print(f"{'─' * 72}")

    # 维度展开
    print("\n  其中:")
    print(f"    每次 get_headers('desktop'): {chrome_details['Chrome Desktop']['subtotal'] + edge_details['subtotal'] + firefox_details['Firefox Desktop']['subtotal'] + safari_details.get('macOS 18.1', {}).get('subtotal', 0) + safari_details.get('macOS 17.6', {}).get('subtotal', 0):,} 种可能")
    print(f"    每次 get_headers('mobile'):  {chrome_details['Chrome Mobile']['subtotal'] + firefox_details['Firefox Mobile']['subtotal'] + safari_details.get('iPhone 18.1', {}).get('subtotal', 0) + safari_details.get('iPhone 17.6', {}).get('subtotal', 0):,} 种可能")
    print(f"    每次 get_headers('tablet'):  {chrome_details['Chrome Tablet']['subtotal'] + safari_details.get('iPad 18.1', {}).get('subtotal', 0) + safari_details.get('iPad 17.6', {}).get('subtotal', 0):,} 种可能")
