# -*- coding: utf-8 -*-
"""标红快讯流水线主程序：采集判红 → LLM 生成 → 渲染图 → SMTP 邮件"""
import json
import os
import sys
import traceback
from pathlib import Path

from eastmoney import fetch_red_news, find_board, board_stocks, is_political
import llm
from render import render_card, fmt_date_cn
from templates import flash_card_html, theme_card_html
from mailer import send

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "out"
STATE = BASE / "state.json"
WINDOW = int(os.environ.get("WINDOW_MINUTES", "12"))
SEND_EMPTY = os.environ.get("SEND_EMPTY", "0") == "1"


def log(msg):
    print(msg, flush=True)


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(state):
    # 只保留最近 2 天，防止无限膨胀
    cutoff = ""
    from datetime import datetime, timedelta
    now = datetime.utcnow() + timedelta(hours=8)
    keep = (now - timedelta(days=2)).strftime("%Y-%m-%d")
    cleaned = {k: v for k, v in state.items() if str(v) >= keep}
    STATE.write_text(json.dumps(cleaned, ensure_ascii=False, indent=1), encoding="utf-8")


STATEMENT = ("特别声明：只做行业科普不作推荐，不对任何人构成投资建议，"
             "资料取材网络仅供参考，不能作为投资依据。理财有风险入市需谨慎！")


def main():
    news, now = fetch_red_news(WINDOW)
    state = load_state()
    fresh = [n for n in news if state.get(n["code"]) != now.strftime("%Y-%m-%d")]
    log(f"window={WINDOW}min red={len(news)} fresh={len(fresh)}")

    if not fresh:
        if SEND_EMPTY:
            send(f"【标红快讯】{now.strftime('%H:%M')} 无新增标红",
                 "<p>本时段无新增标红快讯。</p>", {})
        log("no fresh red news, done")
        return

    OUT.mkdir(exist_ok=True)
    for n in fresh:
        short = f"{n['showTime'].strftime('%H%M')}_{n['code']}"
        card_png = OUT / f"card_{short}.png"
        date_str = fmt_date_cn(n["showTime"])

        if is_political(n["title"]):
            # 时政类：仅卡片图 + 简讯
            render_card(flash_card_html(date_str, n["title"], n["summary"]), str(card_png))
            html = (f"<p><b>{n['title']}</b>（{date_str}）</p><p>{n['summary']}</p>"
                    f"<p><img src='cid:card' style='max-width:100%'></p>")
            send(f"【标红快讯·简讯】{n['title']}｜{n['showTime'].strftime('%H:%M')}",
                 html, {"card": str(card_png)})
            log(f"sent political: {n['title']}")
        else:
            # 财经类：卡片图 + 题材股图×2 + 头条作品
            art = llm.gen_article(n["title"], n["summary"])
            render_card(flash_card_html(date_str, n["title"], n["summary"]), str(card_png))

            theme_pngs = {}
            board = find_board(art.get("board_keyword", ""))
            if board and len(board_stocks(board[0], 1)) >= 8:
                bcode, bname = board
                names = board_stocks(bcode, 16)
                descs = llm.gen_desc(bname, names)
                stocks = [(nm, descs.get(nm, f"{bname}板块成分公司，业务与题材存在产业链关联")) for nm in names]
                half = (len(stocks) + 1) // 2
                p1 = OUT / f"theme1_{short}.png"
                p2 = OUT / f"theme2_{short}.png"
                render_card(theme_card_html("一", "核心梯队", stocks[:half], bname), str(p1))
                if stocks[half:]:
                    render_card(theme_card_html("二", "产业链联动梯队", stocks[half:], bname), str(p2))
                theme_pngs = {"theme1": str(p1)}
                if stocks[half:]:
                    theme_pngs["theme2"] = str(p2)

            imgs = {"card": str(card_png), **theme_pngs}
            theme_html = ""
            if "theme1" in theme_pngs:
                theme_html = ("<p><b>关联题材股 · 核心梯队</b></p>"
                              "<p><img src='cid:theme1' style='max-width:100%'></p>")
                if "theme2" in theme_pngs:
                    theme_html += ("<p><b>关联题材股 · 产业链联动梯队</b></p>"
                                   "<p><img src='cid:theme2' style='max-width:100%'></p>")

            md_text = ("# 备选标题（5选1）\n" +
                       "".join(f"{i}. {t}\n" for i, t in enumerate(art["titles"], 1)) +
                       f"\n{STATEMENT}\n\n## 消息面\n{art['message']}\n" +
                       "".join(f"\n## {v['heading']}\n{v['body']}\n" for v in art["views"]))

            # 结构：备选标题 → 声明 → 消息面（末尾插卡片图）→ 三视角 → 题材股图
            html = (f"<h3>备选标题（5选1）</h3>"
                    f"<ol>{''.join(f'<li>{x}</li>' for x in art['titles'])}</ol>"
                    f"<p>{STATEMENT}</p><h3>消息面</h3>"
                    f"<p>{art['message']}</p>"
                    f"<p><img src='cid:card' style='max-width:100%'></p>"
                    + "".join(f"<h3>{v['heading']}</h3><p>{v['body']}</p>" for v in art["views"])
                    + theme_html)

            send(f"【标红快讯】{n['title']}｜{n['showTime'].strftime('%H:%M')}",
                 html, imgs, md_text)
            log(f"sent finance: {n['title']} board={board[1] if board else 'N/A'}")

        state[n["code"]] = now.strftime("%Y-%m-%d")

    save_state(state)
    log("all done")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
