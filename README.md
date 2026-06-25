# anime-notifier

每部番按其官方播出时间**精确到分钟**推送到个人微信。

零成本：部署在 GitHub Actions，推送走 Server 酱免费版（每个 air_time 触发一次，每天最多 4 条）。
零下载：只通知"刚更新了"，不抓资源。
零状态：不存任何持久化信息，每次推送都是独立的。
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

进入你的仓库 → Settings → Secrets and variables → Actions → New repository secret，添加一个：

| 名称 | 值 |
|---|---|
| `WECHAT_SEND_KEY` | 第 2 步拿到的 SendKey |

> ⚠️ **本版本不需要 PAT**。GitHub Actions 只需要读 checkout，不再 commit state.json（state.json 已删除）。

### 4. 编辑 `config.yaml`

```bash
git clone https://github.com/你的用户名/anime-notifier.git
cd anime-notifier
cp config.example.yaml config.yaml
$EDITOR config.yaml
```

> ⚠️ **`air_time` 字段必填**，格式 `HH:MM`（24 小时制）。
> ```yaml
> schedule:
>   - name: 仙逆
>     weekday: 1          # 1=周一, 7=周日
>     air_time: "10:00"   # 必填，精确到分钟
> wechat:
>   send_key: "${WECHAT_SEND_KEY}"   # 必须用占位符
>   timezone: "Asia/Shanghai"
> ```

`weekday` 编码：`1`=周一, `2`=周二, ..., `7`=周日。
`air_time` 格式：`HH:MM`，例如 `"10:00"`、`"23:30"`。

### 5. 验证

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
python -m anime_notifier --dry-run
```

应该打印类似（取决于当前时间）：

```
🎉 今日追番更新：
📺 完美世界
📺 沧元图 第三季
```

或（无更新时）：

```
💤 今天没有要追的番
```

### 6. Push

```bash
git add config.yaml
git commit -m "feat: 添加我的追番列表"
git push
```

### 7. 手动触发一次 CI 验证

进入仓库 → Actions → anime-notifier → Run workflow，确认 CI 通过、微信收到消息。

> 💡 **手动触发不受时间限制**——任何时候点 Run workflow 都会跑，工具内部按当前真实时间匹配 air_time。

### 8. 等到 air_time 触发

每周对应时间的 cron 触发，CI 跑 1 分钟内推送到微信。

## 加新番

`config.yaml` 加新条目：

```yaml
  - name: 新番
    weekday: 3
    air_time: "20:00"
```

**两种情况**：

- `air_time` 在现有 9 个时间点之内（如 10:00 / 11:00 / 12:00）→ 只需 `git push`，不动 workflow
- `air_time` 是新时间点（如 13:00）→ 改 `config.yaml` + workflow 加一条 cron

## 完结/调整

- **完结某部**：从 `config.yaml` 删除对应条目，`git push`
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

见 [`docs/superpowers/specs/2026-06-25-anime-update-notifier-realtime-design.md`](docs/superpowers/specs/2026-06-25-anime-update-notifier-realtime-design.md)。
