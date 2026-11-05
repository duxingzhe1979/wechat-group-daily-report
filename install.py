# -*- coding: utf-8 -*-
"""一键安装群聊日报 skill 的全部依赖 —— 不需要用户判断装什么。

用法：
    python install.py            # 自动检测并安装缺的东西
    python install.py --check    # 只体检，不安装

做的事情（幂等，可重复运行）：
  0. 检查「微信电脑客户端」是否正在运行并已登录（这一步只能用户自己做）
  1. 检查 Python 版本（wechat-cli 需要 >= 3.11）
  2. pip 安装 wechat-cli / pycryptodome / playwright / av
  3. 检查 Playwright 浏览器（优先用系统 Edge，缺失则自动下载 Chromium）
  4. 首次使用自动执行 wechat-cli init（提取微信密钥）
  5. 检测 CloudBase CLI，缺且本机有 npm 时自动安装
任何一步失败都不会中断整体流程，最后给出汇总。

注意：本工具读的是本机微信 4.x 电脑客户端的本地数据库，密钥只在客户端
登录后加载进内存。所以「微信电脑客户端保持登录」是硬性前提，装依赖解决不了。
"""
import importlib.util
import os
import shutil
import subprocess
import sys

OK, WARN, FAIL, SKIP = "✓", "!", "✗", "-"
PY = sys.executable
results = []


def log(icon, name, msg=""):
    results.append((icon, name, msg))
    print(f"  {icon} {name}{('  ' + msg) if msg else ''}")


def run(cmd, timeout=600):
    """Run a command, return (code, stdout+stderr)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return 127, "command not found"
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def has_module(name):
    return importlib.util.find_spec(name) is not None


# ---------------------------------------------------------------- 0. wechat client
WECHAT_MAIN = {"wechat.exe", "weixin.exe", "wechat", "weixin"}
WECHAT_HELPER = {"wechatappex.exe", "wechatappex"}   # 小程序/内置浏览器进程


def running_wechat():
    """返回 (主客户端进程列表, 辅助进程列表)。Windows 用 tasklist，其它平台用 ps。"""
    main, helper = set(), set()
    if os.name == "nt":
        code, out = run(["tasklist", "/FO", "CSV", "/NH"], timeout=30)
        if code != 0:
            return [], []
        rows = [line.replace('"', "").split(",")[0].strip() for line in out.splitlines()]
    else:
        code, out = run(["ps", "-A", "-o", "comm="], timeout=30)
        if code != 0:
            return [], []
        rows = [os.path.basename(line.strip()) for line in out.splitlines()]
    for name in rows:
        low = name.lower()
        if low in WECHAT_MAIN:
            main.add(name)
        elif low in WECHAT_HELPER:
            helper.add(name)
    return sorted(main), sorted(helper)


def wechat_data_dir():
    """微信 4.x 的数据目录，用来区分「装了没登录」和「根本没装」。"""
    home = os.path.expanduser("~")
    for p in (os.path.join(os.environ.get("APPDATA", ""), "Tencent", "xwechat"),
              os.path.join(home, "Documents", "xwechat_files"),
              os.path.join(home, "Documents", "WeChat Files"),
              "/Applications/WeChat.app"):
        if p and os.path.isdir(p):
            return p
    return ""


def check_wechat_client():
    """硬性前提：微信电脑客户端必须在运行且已登录。失败只能用户自己处理。"""
    main, helper = running_wechat()
    if main:
        log(OK, "微信电脑客户端", f"运行中（{main[0]}）")
        return True
    if helper:
        log(FAIL, "微信电脑客户端", "只检测到小程序进程，主客户端没打开 —— 请打开微信电脑端并登录")
    elif wechat_data_dir():
        log(FAIL, "微信电脑客户端", "未运行/未登录 —— 需要你打开微信电脑端并登录")
    else:
        log(FAIL, "微信电脑客户端", "未检测到 —— 需要 Windows + 微信 4.x 电脑客户端")
    return False


def print_wechat_notice():
    print()
    print("  ┌─ 这一步只能你手动做 ─────────────────────────────┐")
    print("  │ 打开「微信电脑客户端」并登录，保持登录状态。      │")
    print("  │  · 本工具读的是本机电脑端的聊天记录，            │")
    print("  │    手机微信 / 网页版微信 / 企业微信 都不行        │")
    print("  │  · 登录后最小化到托盘即可，窗口不用停在前台      │")
    print("  │  · 只在手机聊过的群，先在电脑上点开该群一次      │")
    print("  │  · 登录后回 Agent 一句「继续」就行，不用重装     │")
    print("  └──────────────────────────────────────────────────┘")
    print()


# ---------------------------------------------------------------- 1. python
def check_python():
    v = sys.version_info
    if v < (3, 11):
        log(FAIL, "Python", f"当前 {v.major}.{v.minor}，需要 3.11+（wechat-cli 要求）")
        return False
    log(OK, "Python", f"{v.major}.{v.minor}.{v.micro}")
    return True


# ---------------------------------------------------------------- 2. pip deps
PYPI_PKGS = [
    ("wechat-cli", None),          # 命令行工具，靠 which 判断
    ("pycryptodome", "Crypto"),
    ("playwright", "playwright"),
    ("av", "av"),
]


def pip_install():
    # 先看哪些真的缺
    missing = [pkg for pkg, mod in PYPI_PKGS if mod and not has_module(mod)]
    if shutil.which("wechat-cli") is None:
        missing.insert(0, "wechat-cli")

    if not missing:
        log(OK, "Python 依赖", "全部已安装")
        return
    print(f"  → 自动安装缺失依赖：{' '.join(missing)}")
    code, out = run([PY, "-m", "pip", "install", "--upgrade", "-q", *missing])
    if code == 0:
        log(OK, "Python 依赖", f"已安装 {', '.join(missing)}")
        return
    # 换清华源重试一次（国内网络）
    print("  → 默认源失败，自动切换清华镜像重试")
    code, out = run([PY, "-m", "pip", "install", "--upgrade", "-q",
                     "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", *missing])
    if code == 0:
        log(OK, "Python 依赖", f"已安装（清华镜像）{', '.join(missing)}")
    else:
        log(FAIL, "Python 依赖", "安装失败，可手动执行：pip install " + " ".join(missing))


# ---------------------------------------------------------------- 3. browser
def ensure_browser():
    """Playwright 包在即可；浏览器优先用系统 Edge，缺了才下载 Chromium。"""
    if not has_module("playwright"):
        log(SKIP, "Playwright 浏览器", "playwright 未装上，跳过")
        return
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            try:
                b = p.chromium.launch(channel="msedge", headless=True)
                b.close()
                log(OK, "Playwright 浏览器", "使用系统 Edge，无需下载")
                return
            except Exception:
                pass
            try:
                b = p.chromium.launch(headless=True)
                b.close()
                log(OK, "Playwright 浏览器", "Chromium 已就绪")
                return
            except Exception:
                pass
    except Exception as e:
        log(WARN, "Playwright 浏览器", f"检测异常：{str(e)[:60]}")

    print("  → 未找到可用浏览器，自动下载 Chromium（约 130MB，仅首次）")
    code, out = run([PY, "-m", "playwright", "install", "chromium"], timeout=1200)
    if code == 0:
        log(OK, "Playwright 浏览器", "Chromium 已下载")
    else:
        log(WARN, "Playwright 浏览器", "下载失败，PNG 长图功能不可用（HTML 日报不受影响）")


# ---------------------------------------------------------------- 4. wechat-cli init
def init_wechat_cli():
    if shutil.which("wechat-cli") is None:
        log(SKIP, "微信数据读取", "wechat-cli 未安装，先解决上面那项")
        return
    code, out = run(["wechat-cli", "sessions", "--limit", "1"], timeout=120)
    if code == 0 and '"chat"' in out:
        log(OK, "微信数据读取", "已就绪")
        return
    if not running_wechat()[0]:
        log(FAIL, "微信数据读取", "读不到数据：微信客户端没在运行/没登录（先登录，再回一句「继续」）")
        return
    print("  → 首次使用，自动提取微信密钥（wechat-cli init）")
    code, out = run(["wechat-cli", "init"], timeout=300)
    if code == 0:
        code2, out2 = run(["wechat-cli", "sessions", "--limit", "1"], timeout=120)
        if code2 == 0:
            log(OK, "微信数据读取", "初始化完成")
        else:
            log(WARN, "微信数据读取", "初始化成功但读取失败，请确认微信已登录并点开过目标群")
    else:
        log(WARN, "微信数据读取", "自动初始化失败：请确认微信桌面端已登录，再运行 wechat-cli init")


# ---------------------------------------------------------------- 5. cloudbase
def ensure_tcb():
    if shutil.which("tcb"):
        log(OK, "CloudBase CLI", "已安装（发布前需 tcb login 扫码一次）")
        return
    npm = shutil.which("npm")
    if not npm:
        log(SKIP, "CloudBase CLI", "本机无 npm，跳过（不影响本地生成 HTML）")
        return
    print("  → 未找到 tcb，自动通过 npm 安装 @cloudbase/cli")
    code, out = run([npm, "install", "-g", "@cloudbase/cli"], timeout=900)
    if code == 0 and shutil.which("tcb"):
        log(OK, "CloudBase CLI", "已安装（发布前需 tcb login 扫码一次）")
    else:
        log(WARN, "CloudBase CLI", "安装失败，可手动：npm i -g @cloudbase/cli")


def main():
    check_only = "--check" in sys.argv
    print("=" * 56)
    print("  群聊日报 skill · 依赖自动安装" + ("（仅体检）" if check_only else ""))
    print("=" * 56)

    ok_py = check_python()
    wechat_ok = check_wechat_client()
    if not wechat_ok:
        print_wechat_notice()

    if check_only:
        for pkg, mod in PYPI_PKGS:
            if mod is None:
                log(OK if shutil.which("wechat-cli") else FAIL, pkg,
                    "已装" if shutil.which("wechat-cli") else "缺失")
            else:
                log(OK if has_module(mod) else FAIL, pkg, "已装" if has_module(mod) else "缺失")
        log(OK if shutil.which("tcb") else FAIL, "tcb", "")
    elif ok_py:
        pip_install()
        ensure_browser()
        init_wechat_cli()
        ensure_tcb()

    print("-" * 56)
    bad = [r for r in results if r[0] == FAIL]
    warn = [r for r in results if r[0] == WARN]
    if not bad and not warn:
        print("  全部就绪，可以直接生成日报了 ✅")
        print("  （提醒：生成期间请保持微信电脑客户端登录，别退出）")
    else:
        print(f"  完成，但有 {len(bad)} 项失败、{len(warn)} 项提醒（见上）")
        if not wechat_ok:
            print("  → 微信电脑客户端那项必须你手动做：打开并登录微信电脑端，")
            print("    然后回 Agent 一句「继续」，不用重装任何东西。")
        print("  把这段输出发给 AI 助手即可继续排查。")
    print("=" * 56)
    return 0 if (not bad and wechat_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
