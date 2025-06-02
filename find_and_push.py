import os
import requests
import yaml
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SUBSCRIBE_URL = os.getenv("SUBSCRIBE_URL")  # 多个地址用英文逗号分隔

def escape_markdown(text):
    """
    转义 MarkdownV2 格式中需要转义的特殊字符
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def get_nodes_from_yaml(yaml_text):
    try:
        data = yaml.safe_load(yaml_text)
        proxies = data.get("proxies", [])
        nodes = []
        for proxy in proxies:
            ptype = proxy.get("type", "未知类型").upper()
            name = proxy.get("name", "未知节点")
            server = proxy.get("server", "")
            port = proxy.get("port", "")
            if ptype == "VMESS":
                uuid = proxy.get("uuid", "")
                alterId = proxy.get("alterId", "")
                network = proxy.get("network", "")
                nodes.append(
                    f"- {ptype} | {name}\n"
                    f"  服务器: {server}:{port}\n"
                    f"  UUID: {uuid}\n"
                    f"  AlterId: {alterId}\n"
                    f"  网络: {network}"
                )
            elif ptype == "TROJAN":
                password = proxy.get("password", "")
                nodes.append(
                    f"- {ptype} | {name}\n"
                    f"  服务器: {server}:{port}\n"
                    f"  密码: {password}"
                )
            elif ptype == "SS":
                cipher = proxy.get("cipher", "")
                password = proxy.get("password", "")
                nodes.append(
                    f"- {ptype} | {name}\n"
                    f"  服务器: {server}:{port}\n"
                    f"  加密方式: {cipher}\n"
                    f"  密码: {password}"
                )
            else:
                nodes.append(f"- {ptype} | {name}\n  服务器: {server}:{port}")
        return nodes
    except Exception as e:
        print("解析 YAML 出错:", e)
        return []

def get_nodes():
    all_nodes = []
    urls = [url.strip() for url in SUBSCRIBE_URL.split(",") if url.strip()]
    for url in urls:
        print(f"拉取订阅：{url}")
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            preview = resp.text[:200].replace("\n", "\\n")
            print("内容预览:", preview)
            nodes = get_nodes_from_yaml(resp.text)
            all_nodes.extend(nodes)
        except Exception as e:
            print(f"订阅抓取失败: {url}\n错误: {e}")
    return all_nodes

def send_message(bot_token, channel_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": channel_id,
        "text": escape_markdown(message),
        "parse_mode": "MarkdownV2"
    }
    try:
        resp = requests.post(url, json=payload)
        if resp.ok:
            print("✅ 消息发送成功")
        else:
            print("❌ 消息发送失败:", resp.text)
    except Exception as e:
        print("❌ 消息异常:", e)

def main():
    if not (BOT_TOKEN and CHANNEL_ID and SUBSCRIBE_URL):
        print("环境变量 BOT_TOKEN、CHANNEL_ID 或 SUBSCRIBE_URL 未设置")
        return

    nodes = get_nodes()
    if not nodes:
        print("没有抓取到任何节点")
        return

    nodes_message = "\n\n".join(nodes[:10])  # 限制最多推送10条
    message = (
        "*🎯 免费 VPN 节点更新（自动）*\n"
        "以下是从多个订阅中整理的节点（仅展示前 10 个）：\n\n"
        f"{nodes_message}"
    )
    send_message(BOT_TOKEN, CHANNEL_ID, message)

if __name__ == "__main__":
    main()
