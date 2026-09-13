# -*- coding: utf-8 -*-
"""Playwright 截图渲染：截图 .card 元素，2 倍清晰度"""
from playwright.sync_api import sync_playwright

WEEKDAY = "一二三四五六日"


def render_card(html: str, out_path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 700, "height": 900}, device_scale_factor=2)
        page.set_content(html, wait_until="networkidle")
        page.locator(".card").screenshot(path=out_path)
        browser.close()


def fmt_date_cn(dt):
    return f"{dt.strftime('%Y-%m-%d')} 星期{WEEKDAY[dt.weekday()]} {dt.strftime('%H:%M')}"
