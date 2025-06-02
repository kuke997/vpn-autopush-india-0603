import os
import requests
import asyncio
import yaml
from telegram import Bot
import urllib.parse

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

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

def get_subscription_country_info(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return None
        data = yaml.safe_load(res.text)
        proxies = data.get("proxies", [])
        countries = set()
        for proxy in proxies:
            country = proxy.get("country")
            if country and isinstance(country, str) and len(country) <= 5:
                countries.add(country.strip())
                continue
            region = proxy.get("region")
            if region and isinstance(region, str) and len(region) <= 5:
                countries.add(region.strip())
                continue
            name = proxy.get("name") or proxy.get("remark") or proxy.get("remarks")
            if name and isinstance(name, str) and len(name) >= 2:
                countries.add(name[:2].strip())
        return ", ".join(sorted(countries)) if countries else None
    except Exception as e:
        print(f"解析节点地区失败：{url}，错误：{e}")
        return None

async def send_to_telegram(bot_token, channel_id, urls):
    if not urls:
        print("❌ 没有可用节点，跳过推送")
        return

    # 只发送前3条
    urls = urls[:3]

    text = (
        "🚀 <b>Best Free VPN for India 2025 — Access Blocked Sites with Clash, V2Ray & Shadowsocks!</b>\n\n"
        "🔥 Use these 100% working free VPN subscription links to bypass internet censorship in India. "
        "These links support Clash, Shadowrocket, V2Ray, and allow high-speed secure access to YouTube, Telegram, Pornhub, Twitter, etc.\n\n"
    )

    for i, url in enumerate(urls, start=1):
        country_info = get_subscription_country_info(url)
        if country_info:
            country_info = f" (Locations: {country_info})"
        else:
            country_info = ""
        safe_url = urllib.parse.quote(url, safe=":/?=&")
        text += f"🔗 <a href=\"{safe_url}\">VPN Link {i}</a>{country_info}\n"

    text += (
        "\n💡 Copy and paste the link into Clash, V2RayN or Shadowrocket.\n"
        "📡 Updated daily. Join our Telegram channel for more: <b>@@vpn4india</b>\n"
        "#FreeVPN #IndiaVPN #UnblockIndia #Clash #V2Ray #TelegramVPN"
    )

    if len(text.encode("utf-8")) > 4000:
        text = text.encode("utf-8")[:4000].decode("utf-8", errors="ignore") + "\n..."

    bot = Bot(token=bot_token)
    try:
        await bot.send_message(
            chat_id=channel_id,
            text=text,
            parse_mode="HTML",  # 避免 ParseMode 引入
            disable_web_page_preview=True
        )
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
    print("🔍 验证 GitHub 搜索到的订阅链接...")
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
