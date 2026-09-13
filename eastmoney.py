# -*- coding: utf-8 -*-
"""东方财富数据：7×24快讯采集 + 概念/行业板块成分股"""
import re
import requests
from datetime import datetime, timedelta

TZ = timedelta(hours=8)  # 北京时间（UTC+8 无夏令时）

FAST_URL = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"
FAST_HEADERS = {"Referer": "https://kuaixun.eastmoney.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BOARD_URL = "https://push2.eastmoney.com/api/qt/clist/get"

POLITICAL = re.compile(r"习近平|李强|外交|国防部|军事|演习|会晤|访问|国务院|中央|军委|航行警告|禁航|发射|火箭")


def fetch_red_news(window_minutes: int):
    """返回窗口内的标红快讯 [{code,title,summary,showTime:datetime}]，已去重"""
    now = datetime.utcnow() + TZ
    seen, result = set(), []
    sort_end = ""
    for _ in range(4):  # 最多翻 4 页
        params = {"client": "web", "biz": "web_724", "fastColumn": "102",
                  "sortEnd": sort_end, "pageSize": "50",
                  "req_trace": now.strftime("%Y%m%d%H%M%S")}
        data = requests.get(FAST_URL, params=params, headers=FAST_HEADERS, timeout=30).json()
        items = (data.get("data") or {}).get("fastNewsList") or []
        if not items:
            break
        oldest = None
        for it in items:
            code = str(it.get("code"))
            if code in seen:
                continue
            seen.add(code)
            t = datetime.strptime(it["showTime"], "%Y-%m-%d %H:%M:%S")
            oldest = t if oldest is None or t < oldest else oldest
            if it.get("titleColor") == 3 and now - t <= timedelta(minutes=window_minutes):
                result.append({"code": code, "title": it["title"].strip(),
                               "summary": (it.get("summary") or "").strip(),
                               "showTime": t})
        if oldest and now - oldest > timedelta(minutes=window_minutes):
            break
        sort_end = (data.get("data") or {}).get("sortEnd") or ""
        if not sort_end:
            break
    result.sort(key=lambda x: x["showTime"])
    return result, now


def find_board(keyword: str):
    """按关键词在东财概念+行业板块中找板块代码，返回 (board_code, board_name) 或 None"""
    if not keyword:
        return None
    codes, names = {}, []
    for fs in ("m:90+t:2", "m:90+t:3"):  # 概念板块 + 行业板块
        try:
            data = requests.get(BOARD_URL, params={
                "pn": 1, "pz": 500, "po": 1, "np": 1, "fltt": 2, "invt": 2,
                "fid": "f12", "fs": fs, "fields": "f12,f14"}, timeout=30).json()
            for d in (data.get("data") or {}).get("diff") or []:
                code, name = str(d.get("f12")), d.get("f14", "")
                codes[name] = code
                names.append(name)
        except Exception:
            continue
    for name in names:  # 完全包含关键词的优先，取名字最短的（最精准）
        if keyword in name:
            return codes[name], name
    return None


def board_stocks(board_code: str, limit: int = 16):
    """板块成分股名称（按涨跌幅排序取前 limit）"""
    try:
        data = requests.get(BOARD_URL, params={
            "pn": 1, "pz": limit, "po": 1, "np": 1, "fltt": 2, "invt": 2,
            "fid": "f3", "fs": f"b:{board_code}", "fields": "f12,f14"}, timeout=30).json()
        diff = (data.get("data") or {}).get("diff") or []
        return [d.get("f14", "") for d in diff if d.get("f14")][:limit]
    except Exception:
        return []


def is_political(title: str) -> bool:
    return bool(POLITICAL.search(title))
