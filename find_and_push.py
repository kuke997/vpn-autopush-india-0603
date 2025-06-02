import os
import requests
from telegram import Bot
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# 预定义的免费订阅链接列表
SUBSCRIBE_URLS = [
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

# 转义 MarkdownV2 特殊字符
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def validate_subscription(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and "proxies" in res.text:
            return True
    except:
        pass
    return False

def send_to_telegram(bot_token, channel_id, urls):
    if not urls:
        print("没有可用节点")
        return

    # 转义所有 URL 防止 Markdown 失败
    escaped_urls = [escape_markdown(url) for url in urls[:20]]
    text = "*🆕 免费节点订阅更新：*\n\n" + "\n".join(escaped_urls)

    bot = Bot(token=bot_token)
    try:
        bot.send_message(chat_id=channel_id, text=text, parse_mode="MarkdownV2")
        print("✅ 推送成功")
    except Exception as e:
        print("❌ 推送失败:", e)

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("环境变量 BOT_TOKEN 或 CHANNEL_ID 未设置")
        return

    print("🔍 正在验证预定义的订阅链接...")
    valid_urls = [url for url in SUBSCRIBE_URLS if validate_subscription(url)]
    print(f"✔️ 验证通过链接数: {len(valid_urls)}")

    with open("valid_links.txt", "w") as f:
        for link in valid_urls:
            f.write(link + "\n")

    print("📄 已保存到 valid_links.txt")
    send_to_telegram(BOT_TOKEN, CHANNEL_ID, valid_urls)

if __name__ == "__main__":
    main()
