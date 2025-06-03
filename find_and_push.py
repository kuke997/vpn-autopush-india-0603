import os
import requests
import asyncio
import yaml
from telegram import Bot
import urllib.parse
import re

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
    print("🔍 Searching GitHub for subscription files...")
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
        print(f"✨ Found {len(links)} potential links.")
        return links
    except Exception as e:
        print("GitHub search failed:", e)
        return []

# 只保留 emoji 和英文
def clean_country_info(text):
    if not text:
        return None
    emoji_pattern = re.compile("[\U0001F1E6-\U0001F1FF]{2}")
    english_pattern = re.compile(r'[A-Za-z]{2,}')
    emojis = emoji_pattern.findall(text)
    english = english_pattern.findall(text)
    return " ".join(emojis + english) if (emojis or english) else None

def get_subscription_country_info(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return None
        data = yaml.safe_load(res.text)
        proxies = data.get("proxies", [])
        countries = set()
        for proxy in proxies:
            for key in ["country", "region", "name", "remark", "remarks"]:
                val = proxy.get(key)
                if val and isinstance(val, str):
                    cleaned = clean_country_info(val.strip())
                    if cleaned:
                        countries.add(cleaned)
        return ", ".join(sorted(countries)) if countries else None
    except Exception as e:
        print(f"Failed to parse regions from: {url}, error: {e}")
        return None

async def send_to_telegram(bot_token, channel_id, urls):
    if not urls:
        print("❌ No valid links found.")
        return

    urls = urls[:3]

    link_lines = ""
    for i, url in enumerate(urls, start=1):
        country_info = get_subscription_country_info(url)
        country_text = f" (🌐 {country_info})" if country_info else ""
        safe_url = urllib.parse.quote(url, safe=":/?=&")
        link_lines += f"🔗 <a href=\"{safe_url}\">VPN Link {i}</a>{country_text}\n"

    final_text = (
        "🌍 <b>भारत 🇮🇳 के लिए बेस्ट 3 फ्री VPNs (Top 3 Free VPNs for India – 2025)</b>\n"
        "🔓 <b>Clash, V2Ray और Shadowsocks से वेबसाइट्स और ऐप्स अनब्लॉक करें।</b>\n\n"
        "📺 YouTube, Telegram, X (Twitter), Pornhub और बाकी सभी साइट्स काम करेंगी!\n"
        "✅ कोई साइनअप नहीं – Fast, Safe, और Anonymous।\n\n"
        f"{link_lines}\n"
        "📲 इन लिंक्स को Clash, Shadowrocket, या V2RayN ऐप में डालें।\n"
        "🕒 डेली अपडेट। लेटेस्ट फ्री VPNs के लिए हमारा Telegram जॉइन करें: <a href=\"https://t.me/vpn4india\">@vpn4india</a>\n\n"
        "#IndiaVPN #FreeVPN #ClashVPN #V2Ray #UnblockIndia #TelegramVPN"
    )

    if len(final_text.encode("utf-8")) > 4000:
        final_text = final_text.encode("utf-8")[:4000].decode("utf-8", errors="ignore") + "\n..."

    bot = Bot(token=bot_token)
    try:
        await bot.send_message(
            chat_id=channel_id,
            text=final_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        print("✅ Sent successfully.")
    except Exception as e:
        print("❌ Failed to send message:", e)

async def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("BOT_TOKEN or CHANNEL_ID environment variables not set.")
        return

    print("🔍 Validating static subscription links...")
    valid_static = [url for url in STATIC_SUBSCRIBE_URLS if validate_subscription(url)]

    github_links = search_github_clash_urls()
    print("🔍 Validating GitHub-discovered subscription links...")
    valid_dynamic = [url for url in github_links if validate_subscription(url)]

    all_valid = valid_static + valid_dynamic
    print(f"✔️ Total valid links: {len(all_valid)}")

    with open("valid_links.txt", "w") as f:
        for link in all_valid:
            f.write(link + "\n")
    print("📄 Saved to valid_links.txt")

    await send_to_telegram(BOT_TOKEN, CHANNEL_ID, all_valid)

if __name__ == "__main__":
    asyncio.run(main())
