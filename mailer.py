# -*- coding: utf-8 -*-
"""SMTP 邮件：图片以内嵌 CID 方式插入正文（长期有效，无链接过期问题）"""
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


def send(subject: str, html: str, images: dict, md_text: str = None):
    """images: {cid: png文件路径}；md_text 可选，作为 .md 附件"""
    msg = MIMEMultipart("related")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = formataddr(("快讯助手", os.environ["SMTP_USER"]))
    msg["To"] = os.environ.get("MAIL_TO", os.environ["SMTP_USER"])

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html, "html", "utf-8"))
    msg.attach(alt)

    for cid, path in images.items():
        with open(path, "rb") as f:
            img = MIMEImage(f.read())
        img.add_header("Content-ID", f"<{cid}>")
        img.add_header("Content-Disposition", "inline", filename=os.path.basename(path))
        msg.attach(img)

    if md_text:
        att = MIMEApplication(md_text.encode("utf-8"))
        att.add_header("Content-Disposition", "attachment",
                       filename=Header("头条作品.md", "utf-8").encode())
        msg.attach(att)

    with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=60) as s:
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        s.send_message(msg)
