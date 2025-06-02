# Auto Free VPN Push

自动搜索 GitHub 上的免费 Clash 订阅节点，合并预定义免费订阅，自动验证有效性，每小时自动推送最新有效节点到 Telegram 频道。

## 部署步骤

1. Fork 本仓库或直接使用。

2. 在 GitHub 仓库 Settings > Secrets 中添加以下 Secrets：
   - `BOT_TOKEN`：Telegram Bot Token
   - `CHANNEL_ID`：Telegram 频道 ID（格式为 @channelusername 或频道数字 ID）
   - `GITHUB_TOKEN`（可选）：GitHub 个人访问令牌，提升 API 限额

3. 工作流已自动配置，每小时运行一次，可手动触发。

4. 查看 Telegram 频道，接收推送的免费节点订阅链接。

## 依赖

- python-telegram-bot
- requests
