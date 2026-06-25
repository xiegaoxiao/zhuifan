# anime-notifier

每天 20:00（北京时间）把当日追番更新推送到个人微信。

零成本：部署在 GitHub Actions，推送走 Server 酱免费版（攒批推送，1 条/天，永远不超 5 条/天额度）。
零下载：只通知"今天更新了第几集"，不抓资源。
零运维：写好配置后基本不用管。

## 5 分钟上手

### 1. 创建仓库

点本仓库右上角 "Use this template" 创建一个新仓库（设为 Public 或 Private 都行）。

### 2. 拿 Server 酱 SendKey

1. 打开 [sct.ftqq.com](https://sct.ftqq.com)
2. 用 GitHub 账号登录
3. 微信扫码关注"方糖"服务号
4. 复制页面上的 SendKey（形如 `SCT123456_AbCdEfGh`）

### 3. 配 GitHub Secrets

进入你的仓库 → Settings → Secrets and variables → Actions → New repository secret，添加两个：

| 名称 | 值 |
|---|---|
| `WECHAT_SEND_KEY` | 第 2 步拿到的 SendKey |
| `ACTIONS_TOKEN` | 一个**Classic** GitHub PAT（[点这里创建](https://github.com/settings/tokens/new)），**Expiration** 选 `No expiration`，**Scopes** **必须**勾 ✅ `repo`（"Full control of private repositories"） |

> ⚠️ **PAT 三件套必做**：
> 1. 创建时勾 `repo`（默认不勾，只勾了 public_repo 是不够的）
> 2. 创建后**先在本地测 push**：`git clone https://<你的PAT>@github.com/<用户名>/<仓库>.git test && cd test && echo ok >> README.md && git push && cd .. && rm -rf test`，能成功再继续
> 3. 填到 Secrets 时**不要带前后空格/换行**（密码管理器粘贴容易带）

### 4. 编辑 `config.yaml`

```bash
git clone https://github.com/你的用户名/anime-notifier.git
cd anime-notifier
cp config.example.yaml config.yaml
$EDITOR config.yaml
```

> ⚠️ **必须**把 `send_key:` 改成占位符（**绝对不能**直接填 SendKey 进 git 历史）：
> ```yaml
> wechat:
>   send_key: "${WECHAT_SEND_KEY}"   # 占位符，CI 时自动注入
> ```

`weekday` 编码：`1`=周一, `2`=周二, ..., `7`=周日。

### 5. 验证

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
python -m anime_notifier --dry-run
```

应该打印一条类似这样的消息（取决于当天周几）：

```
🎉 今日追番更新：
📺 进击的巨人 最终季  第 1 集
```

### 6. Push

```bash
git add config.yaml
git commit -m "feat: 添加我的追番列表"
git push
```

### 7. 手动触发一次 CI 验证

进入仓库 → Actions → anime-notifier → Run workflow，确认 CI 通过、微信收到消息。

### 8. 等第二天 20:00

每天北京时间 20:00 自动触发。

## 完结/调整

- **加新番**：编辑 `config.yaml` 加一行 `git push`
- **完结某部**：从 `config.yaml` 删除该条目（`state.json` 里的旧记录无害保留，工具会自动跳过）
- **临时停推**：仓库 → Settings → Actions → disable workflow

## 本地开发

```bash
# 跑全部测试
python -m pytest -v

# dry-run
python -m anime_notifier --dry-run

# 真实推送（需要本地有真实 SendKey）
python -m anime_notifier
```

## 架构

见 [`docs/superpowers/specs/2026-06-25-anime-update-notifier-design.md`](docs/superpowers/specs/2026-06-25-anime-update-notifier-design.md)。
