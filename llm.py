# -*- coding: utf-8 -*-
"""GLM（智谱 BigModel）LLM 调用与提示词"""
import json
import os
import re

import requests

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
BANNED = ["国产化", "信创", "央企", "国企", "证监局", "政府"]


def chat(messages, temperature=0.7):
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {os.environ['GLM_API_KEY']}"},
        json={
            "model": os.environ.get("GLM_MODEL", "glm-4-flash"),
            "messages": messages,
            "temperature": temperature,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def parse_json(text):
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


def sanitize(text):
    """敏感词兜底替换（符合用户禁用词规则）"""
    for w in BANNED:
        text = text.replace(w, "行业监管")
    return text


ARTICLE_PROMPT = """你是财经科普作者，根据一条快讯写一篇今日头条风格的作品。只依据快讯给出的事实写作，不得编造具体数字（如提价幅度、业绩数字）。

快讯标题：{title}
快讯正文：{summary}

严格输出 JSON（不要 markdown 代码块），结构：
{{
  "board_keyword": "用于在东方财富概念/行业板块中搜索关联板块的2-6字关键词（如：染料、稀土、光伏）",
  "titles": ["标题1", "标题2", "标题3", "标题4", "标题5"],
  "message": "消息面段落",
  "views": [
    {{"heading": "从XX视角看", "body": "段落正文"}},
    {{"heading": "从XX视角看", "body": "段落正文"}},
    {{"heading": "从XX视角看", "body": "段落正文"}}
  ]
}}

要求：
- titles：5个备选爆款标题，各约25字，带"A股名单/受益公司/拐点"类钩子，不出现具体涨跌预测数字
- message：以"据报道，"开头，只转述快讯事实，段尾加"（东方财富）"
- views：三段，角度建议为供需/行业格局/产业链传导与投资映射，每段200-300字
- 全文不得出现：具体来源时间、"标红"字样、股票代码；不得出现"国产化、信创、央企、国企、证监局、政府"等词（涉客户用"大型企业/行业客户"）；不承诺收益、不给出买卖指令
- 点名公司仅限快讯正文中出现的公司
"""

DESC_PROMPT = """以下是A股公司名单，题材是「{theme}」。请为每家公司写一句题材关联度描述。

公司名单：{names}

严格输出 JSON（不要 markdown 代码块）：{{"公司名": "描述", ...}}

要求：
- 每条描述40-50字，讲清该公司业务与题材的关联逻辑（主营产品、产业链位置、受益方式）
- 只描述其公开已知的主营业务，不虚构关联；与题材无明显关联的公司，如实描述其中性业务定位
- 不写股价、涨跌幅、业绩数字；不用"国产化、信创、央企、国企"等词
"""


def gen_article(title, summary):
    raw = chat([{"role": "user", "content": ARTICLE_PROMPT.format(title=title, summary=summary)}])
    data = parse_json(raw)
    data["message"] = sanitize(data["message"])
    for v in data["views"]:
        v["body"] = sanitize(v["body"])
    for i, t in enumerate(data["titles"]):
        data["titles"][i] = sanitize(t)
    return data


def gen_desc(theme, names):
    raw = chat([{"role": "user", "content": DESC_PROMPT.format(theme=theme, names="、".join(names))}])
    return {sanitize(k): sanitize(v) for k, v in parse_json(raw).items()}
