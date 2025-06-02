import os
import requests
import re
import time
from telegram import Bot

# 配置
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
KEYWORDS = ["clash", "yaml", "sub", "节点", "订阅"]
GITHUB_SEARCH_URL = "https://api.github.com/search/code?q=clash+in:file+language:YAML"

def search_github_subscriptions():
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    urls = set()

    print("🔍 正在搜索 GitHub 上的 Clash 配置链接...")
    try:
        for page in range(1, 3):  # 控制搜索页数
            res = requests.get(f"{GITHUB_SEARCH_URL}&page={page}", headers=headers)
            data = res.json()
            for item in data.get("items", []):
                html_url = item["html_url"]
                raw_url = html_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                if raw_url.endswith((".yaml", ".yml")):
                    urls.add(raw_url)
            time.sleep(2)
    except Exception as e:
        print("❌ GitHub 搜索失败:", e)
    return list(urls)

def validate_subscription(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and "proxies" in res.text:
            return True
    except:
        return False
    return False

def send_to_telegram(bot_token, channel_id, urls):
    if not urls:
        print("没有可用节点")
        return

    text = "*🆕 免费节点订阅更新：*\n\n" + "\n".join(urls[:20])
    bot = Bot(token=bot_token)
    try:
        bot.send_message(chat_id=channel_id, text=text, parse_mode="Markdown")
        print("✅ 推送成功")
    except Exception as e:
        print("❌ 推送失败:", e)

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("环境变量 BOT_TOKEN 或 CHANNEL_ID 未设置")
        return

    all_urls = search_github_subscriptions()
    print(f"共找到 {len(all_urls)} 条链接，开始验证...")

    valid_urls = [url for url in all_urls if validate_subscription(url)]
    print(f"✔️ 验证通过链接数: {len(valid_urls)}")

    send_to_telegram(BOT_TOKEN, CHANNEL_ID, valid_urls)

if __name__ == "__main__":
    main()
