# -*- coding: utf-8 -*-
"""HTML → 长图 PNG（playwright；优先系统 Edge，缺失自动降级 Chromium）"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

files = sys.argv[1:]
if not files:
    sys.exit('用法: python html2png.py <a.html> [b.html ...]')


def launch(p):
    """Edge 优先（Windows 自带，免下载）；失败则回落到 Chromium。"""
    for kwargs in ({'channel': 'msedge'}, {}):
        try:
            return p.chromium.launch(headless=True, **kwargs)
        except Exception:
            continue
    sys.exit('没有可用浏览器，请先运行: python install.py')


with sync_playwright() as p:
    browser = launch(p)
    page = browser.new_page(viewport={'width': 860, 'height': 1200}, device_scale_factor=2)
    for f in files:
        absf = os.path.abspath(f)
        page.goto('file:///' + absf.replace('\\', '/'), wait_until='networkidle')
        page.wait_for_timeout(600)
        out = absf[:-5] + '.png' if absf.endswith('.html') else absf + '.png'
        page.screenshot(path=out, full_page=True)
        print('OK', os.path.basename(out), f'{os.path.getsize(out)//1024}KB')
    browser.close()
