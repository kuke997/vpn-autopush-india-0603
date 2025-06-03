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
        print(f"Failed to parse regions from: {url}, error: {e}")
        return None

async def send_to_telegram(bot_token, channel_id, urls):
    if not urls:
        print("❌ No valid links found.")
        return

    urls = urls[:3]  # Only send top 3

    link_lines = ""
    for i, url in enumerate(urls, start=1):
        country_info = get_subscription_country_info(url)
        if country_info:
            country_info = f" (Location: {country_info})"
        else:
            country_info = ""
        safe_url = urllib.parse.quote(url, safe=":/?=&")
        link_lines += f"🔗 <a href=\"{safe_url}\">VPN Link {i}</a>{country_info}\n"

    text_en = (
        "🌍 <b>Top 3 Free VPNs for India (2025)</b>\n"
        "🔓 <b>Unblock websites, apps, and videos using Clash, V2Ray, and Shadowsocks!</b>\n\n"
        "🇮🇳 Perfect for YouTube, Telegram, X (Twitter), Pornhub, and more.\n"
        "✅ No signup needed – fast, safe, and anonymous.\n\n"
        f"{link_lines}\n"
        "📲 Use these links in Clash, Shadowrocket, or V2RayN.\n"
        "🕒 Updated every day. Join our Telegram for latest free VPNs: <a href=\"https://t.me/vpn4india\">@vpn4india</a>\n\n"
        "#IndiaVPN #FreeVPN #ClashVPN #V2Ray #UnblockIndia #TelegramVPN"
    )

    text_hi = (
        "🌍 <b>भारत के लिए टॉप 3 फ्री VPNs (2025)</b>\n"
        "🔓 <b>Clash, V2Ray और Shadowsocks की मदद से वेबसाइट और ऐप्स का अनब्लॉक करें!</b>\n\n"
        "🇮🇳 YouTube, Telegram, X (Twitter), Pornhub और अन्य साइट्स के लिए परफेक्ट।\n"
        "✅ बिना रजिस्ट्रेशन – तेज़, सुरक्षित और गुमनाम।\n\n"
        f"{link_lines}\n"
        "📲 इन लिंक्स को Clash, Shadowrocket, या V2RayN में इस्तेमाल करें।\n"
        "🕒 हर दिन अपडेट होता है। लेटेस्ट फ्री VPNs के लिए हमारा Telegram चैनल जॉइन करें: <a href=\"https://t.me/vpn4india\">@vpn4india</a>\n\n"
        "#IndiaVPN #FreeVPN #ClashVPN #V2Ray #UnblockIndia #TelegramVPN"
    )

    final_text = text_en + "\n\n" + text_hi

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
