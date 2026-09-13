# -*- coding: utf-8 -*-
"""HTML 模板：快讯卡片 + 题材股卡片（与本地 WorkBuddy 版式一致）"""
import math


def flash_card_html(date_str: str, title: str, content: str) -> str:
    """快讯卡片。date_str: 'YYYY-MM-DD 星期X HH:mm'"""
    title_lines = max(1, math.ceil(len(title) / 13))
    content_lines = max(2, math.ceil(len(content) / 15))
    height = 232 + 40 + 46 + 36 + title_lines * 66 + 100 + content_lines * 70 + 140
    height = max(980, min(1600, height))
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: 674px; background: #fff; font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif; }}
  .card {{ width: 674px; height: {height}px; overflow: hidden; position: relative; background: #fff; }}
  .header {{ position: relative; height: 232px;
    background: linear-gradient(135deg, #e8342a 0%, #d81e06 55%, #b31500 100%); overflow: hidden; }}
  .globe {{ position: absolute; border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, rgba(255,255,255,.28), rgba(255,255,255,.05) 60%, transparent 70%);
    border: 1px solid rgba(255,255,255,.18); }}
  .g1 {{ width: 300px; height: 300px; left: -90px; top: 20px; }}
  .g2 {{ width: 190px; height: 190px; right: -50px; bottom: -70px;
    background: radial-gradient(circle at 40% 35%, rgba(255,255,255,.22), transparent 65%); }}
  .g3 {{ width: 90px; height: 90px; right: 120px; top: 26px;
    background: radial-gradient(circle at 40% 35%, rgba(255,255,255,.16), transparent 65%); }}
  .swoosh {{ position: absolute; width: 420px; height: 420px; right: -160px; top: -190px; border-radius: 50%;
    border: 26px solid rgba(255,255,255,.10); border-left-color: transparent; border-bottom-color: transparent;
    transform: rotate(35deg); }}
  .swoosh2 {{ position: absolute; width: 300px; height: 300px; left: -120px; bottom: -170px; border-radius: 50%;
    border: 20px solid rgba(255,255,255,.08); border-right-color: transparent; border-top-color: transparent;
    transform: rotate(20deg); }}
  .brand {{ position: absolute; left: 0; right: 0; top: 74px; text-align: center;
    color: #fff; font-size: 76px; font-weight: 900; letter-spacing: 6px;
    text-shadow: 0 4px 14px rgba(120,0,0,.35); }}
  .brand .dot {{ color: #ffe9a8; }}
  .brand-sub {{ position: absolute; left: 0; right: 0; top: 168px; text-align: center;
    color: rgba(255,255,255,.85); font-size: 22px; letter-spacing: 10px; }}
  .body-wrap {{ padding: 40px 44px 0 44px; position: relative; }}
  .date {{ color: #8a8a8a; font-size: 30px; letter-spacing: 1px; }}
  .title {{ margin-top: 36px; color: #e02b1d; font-size: 44px; font-weight: 800; line-height: 1.5; letter-spacing: 1px; }}
  .quote {{ margin-top: 34px; height: 60px; position: relative; }}
  .quote::before {{ content: "\\201C"; position: absolute; left: -6px; top: -34px;
    font-size: 150px; font-weight: 900; color: #f8d2cd; font-family: Georgia, serif; line-height: 1; }}
  .content {{ margin-top: 6px; color: #4a4a4a; font-size: 36px; font-weight: 600; line-height: 1.95; text-align: justify; }}
  .content .src {{ color: #9a9a9a; font-weight: 400; }}
  .wm-l, .wm-r {{ position: absolute; top: 480px; width: 26px; height: 560px; overflow: hidden; opacity: .55; }}
  .wm-l {{ left: 6px; }} .wm-r {{ right: 6px; }}
  .wm-l span, .wm-r span {{ display: block; writing-mode: vertical-rl; color: #f3b9b3; font-size: 24px;
    letter-spacing: 8px; font-weight: 700; white-space: nowrap; }}
</style></head>
<body><div class="card">
  <div class="header"><div class="globe g1"></div><div class="globe g2"></div><div class="globe g3"></div>
    <div class="swoosh"></div><div class="swoosh2"></div>
    <div class="brand">东方财富<span class="dot">·</span>快讯</div>
    <div class="brand-sub">7×24 财经快讯</div>
  </div>
  <div class="body-wrap">
    <div class="date">{date_str}</div>
    <div class="title">{title}</div>
    <div class="quote"></div>
    <div class="content">{content} <span class="src">（东方财富）</span></div>
  </div>
  <div class="wm-l"><span>财 经 快 讯 速 递</span></div>
  <div class="wm-r"><span>财 经 快 讯 速 递</span></div>
</div></body></html>"""


def theme_card_html(no: str, tag: str, stocks: list, title_prefix: str) -> str:
    """题材股卡片。stocks: [(name, desc40_50字)]"""
    n = len(stocks)
    height = max(600, 190 + 26 + n * 148 + 60)
    rows = []
    for i, (name, desc) in enumerate(stocks, 1):
        rows.append(f"""    <div class="row">
      <div class="rank">{i}</div>
      <div class="mid"><div class="name">{name}</div>
        <div class="desc">{desc}</div></div>
    </div>""")
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ width:674px; background:#fff; font-family:"Microsoft YaHei","PingFang SC","Noto Sans CJK SC",sans-serif; }}
  .card {{ width:674px; height:{height}px; overflow:hidden; background:#fff; position:relative; }}
  .header {{ position:relative; height:190px;
    background:linear-gradient(135deg,#e8342a 0%,#d81e06 55%,#b31500 100%); overflow:hidden; }}
  .g1 {{ position:absolute; width:280px; height:280px; border-radius:50%; left:-80px; top:10px;
    background:radial-gradient(circle at 35% 30%, rgba(255,255,255,.25), transparent 65%);
    border:1px solid rgba(255,255,255,.18); }}
  .g2 {{ position:absolute; width:170px; height:170px; border-radius:50%; right:-40px; bottom:-70px;
    background:radial-gradient(circle at 40% 35%, rgba(255,255,255,.2), transparent 65%); }}
  .brand {{ position:absolute; left:0; right:0; top:44px; text-align:center; color:#fff;
    font-size:58px; font-weight:900; letter-spacing:5px; text-shadow:0 3px 10px rgba(120,0,0,.35); }}
  .brand .dot {{ color:#ffe9a8; }}
  .brand-sub {{ position:absolute; left:0; right:0; top:122px; text-align:center;
    color:rgba(255,255,255,.9); font-size:24px; letter-spacing:6px; font-weight:700; }}
  .list {{ padding:26px 34px 0 34px; }}
  .row {{ display:flex; align-items:flex-start; padding:15px 0; border-bottom:1px dashed #eee; }}
  .row:last-child {{ border-bottom:none; }}
  .rank {{ flex:none; width:44px; font-size:30px; font-weight:900; color:#d81e06; padding-top:8px; }}
  .mid {{ flex:1; padding-right:4px; }}
  .name {{ font-size:30px; font-weight:800; color:#222; }}
  .desc {{ font-size:22px; color:#555; line-height:1.55; margin-top:6px; }}
  .foot {{ position:absolute; bottom:14px; left:0; right:0; text-align:center;
    font-size:18px; color:#bbb; letter-spacing:2px; }}
</style></head>
<body><div class="card">
  <div class="header"><div class="g1"></div><div class="g2"></div>
    <div class="brand">题材股<span class="dot">·</span>雷达</div>
    <div class="brand-sub">{title_prefix}关联标的（{no}）｜{tag}</div>
  </div>
  <div class="list">
{chr(10).join(rows)}
  </div>
  <div class="foot">来源：东方财富 · 仅为题材梳理，不构成投资建议</div>
</div></body></html>"""
