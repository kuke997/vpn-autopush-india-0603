import os
import requests
import asyncio
from telegram import Bot
import html

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# 免费订阅链接（你可以继续添加）
STATIC_SUBSCRIBE_URLS = [
    "https://wanmeiwl3.xyz/gywl/4e3979fc330fc6b7806f3dc78a696f10",
    "https://bestsub.bestrui.ggff.net/share/bestsub/cdcefaa4-1f0d-462e-ba76-627b344989f2/all.yaml",
    "https://linuxdo.miaoqiqi.me/linuxdo/love",
    "https://bh.jiedianxielou.workers.dev",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/clash.yaml",
    "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/clash.yml",
    "https://cdn.jsdelivr.net/gh/vxiaov/free_proxies@main/clash/clash.provider.yaml",
    "https://freenode.openrunner.net/uploads/20240617-clash.yaml",
    "https://tt.vg/freeclash",
    "https://raw.githubusercontent.com/SnapdragonLee/SystemProxy/master/dist/clash_config.yaml"
]

def validate_subscription(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and "proxies" in res.text:
            return True
    except:
        pass
    return False

def search_github_clash_urls():
    print("🔍 GitHub 搜索订阅文件中...")
    try:
        headers = {
            "Accept": "application/vnd.github.v3.text-match+json"
        }
        query = "clash filename:clash.yaml in:path extension:yaml"
        url = f"https://api.github.com/search/code?q={query}&per_page=100"
        res = requests.get(url, headers=headers, timeout=15)
        items = res.json().get("items", [])
        links = []
        for item in items:
            raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            links.append(raw_url)
        print(f"✨ GitHub 搜索到 {len(links)} 个可能的订阅链接")
        return links
    except Exception as e:
        print("GitHub 搜索失败:", e)
        return []

async def send_to_telegram(bot_token, channel_id, urls):
    if not urls:
        print("❌ 没有可用节点，跳过推送")
        return

    # 使用 HTML 格式避免 Markdown 错误
    safe_links = [f"<code>{html.escape(url)}</code>" for url in urls[:20]]
    text = "<b>🆕 免费节点订阅更新（自动验证）</b>\n\n" + "\n".join(safe_links)

    if len(text.encode('utf-8')) > 4000:
        text = text.encode("utf-8")[:4000].decode("utf-8", errors="ignore") + "\n..."

    bot = Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=channel_id, text=text, parse_mode="HTML", disable_web_page_preview=True)
        print("✅ 推送成功")
    except Exception as e:
        print("❌ 推送失败:", e)

async def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("环境变量 BOT_TOKEN 或 CHANNEL_ID 未设置")
        return

    print("🔍 验证预定义订阅链接...")
    valid_static = [url for url in STATIC_SUBSCRIBE_URLS if validate_subscription(url)]

    github_links = search_github_clash_urls()
    print("🔍 验证GitHub搜索到的订阅链接...")
    valid_dynamic = [url for url in github_links if validate_subscription(url)]

    all_valid = valid_static + valid_dynamic
    print(f"✔️ 共验证通过的有效订阅链接数量: {len(all_valid)}")

    with open("valid_links.txt", "w") as f:
        for link in all_valid:
            f.write(link + "\n")
    print("📄 已保存到 valid_links.txt")

    await send_to_telegram(BOT_TOKEN, CHANNEL_ID, all_valid)

if __name__ == "__main__":
    asyncio.run(main())
