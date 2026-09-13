# 标红快讯推送机器人（GitHub Actions 版）

每 10 分钟抓取东方财富 7×24 快讯，筛出标红（`titleColor=3`）条目，自动生成快讯卡片图 + 题材股图×2 + 头条作品，通过 QQ 邮箱 SMTP 发送到你的邮箱。**电脑关机也照常运行。**

## 部署步骤（约 10 分钟）

### 1. 创建私有仓库并上传代码

```bash
# 在 flash-news-bot 目录下执行
git init
git add .
git commit -m "init: flash news pipeline"
# 在 GitHub 网页上新建一个 Private 仓库（如 flash-news-bot），然后：
git remote add origin https://github.com/<你的用户名>/flash-news-bot.git
git branch -M main
git push -u origin main
```

### 2. 配置 Secrets（仓库 Settings → Secrets and variables → Actions）

| 名称 | 类型 | 说明 |
|---|---|---|
| `SMTP_USER` | Secret | 你的邮箱，如 `boriscai@foxmail.com` |
| `SMTP_PASS` | Secret | QQ 邮箱 SMTP 授权码（不是密码！QQ邮箱 → 设置 → 账号 → 开启 SMTP 服务 → 生成授权码） |
| `GLM_API_KEY` | Secret | 智谱 BigModel API Key（生成头条作品和题材描述用） |
| `MAIL_TO` | Variable（可选） | 收件邮箱，默认同 SMTP_USER |

### 3. 开启工作流写权限

仓库 Settings → Actions → General → Workflow permissions → 选 **Read and write permissions**（state.json 去重需要回写仓库）。

### 4. 手动测试一次

Actions 页 → flash-news-pipeline → Run workflow → 运行。查看日志确认：
- `red=N fresh=N`（本窗口标红数量）
- `sent finance/political: ...`（发送成功）
- 无标红时输出 `no fresh red news, done`（不发邮件）

## 运行时段说明（重要）

默认 cron 只在**交易日盘中**（北京时间 9:00–15:50）运行——这是私有仓库免费额度（2000 分钟/月）内能承受的最高频率。标红快讯绝大多数出现在盘中，晚上/周末的标红很少且不紧急。

如需 7×24 小时覆盖，两个办法：
1. 把仓库改成 **Public**（公共仓库 Actions 完全免费不限时长），把 cron 改成 `*/10 * * * *`；
2. 私有仓库付费额度（按量计费）。

改时段：编辑 `.github/workflows/flash-news.yml` 里 cron 的 UTC 小时范围（北京时间 = UTC+8）。

## 注意事项

- **GitHub 定时任务不精确**：高峰期可能延迟几分钟到十几分钟，属正常现象；脚本窗口设 12 分钟 + state 去重，不会漏推或重推。
- **60 天不活跃停用**：GitHub 会停用 60 天无提交的定时工作流；本流程每次有标红都会回写 state.json，长期无标红时手动 Run 一次即可续期。
- **时政类标红**：自动识别（外交/军事/领导人等关键词），只发卡片图+简讯，不套投资模板。
- **题材股图**：自动在东财概念/行业板块中匹配关键词查成分股，匹配不到板块时自动跳过题材图（只发卡片图+作品），不会硬凑。
- 内容合规：作品由 GLM 按固定提示词生成，内置敏感词兜底替换与"不构成投资建议"声明。

## 本地调试（可选）

```bash
pip install -r requirements.txt
playwright install chromium
set GLM_API_KEY=xxx & set SMTP_USER=xxx & set SMTP_PASS=xxx
python flash_news/pipeline.py
```
