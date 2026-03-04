import os, requests
from huggingface_hub import HfApi

def send_to_wechat(msg):
    token = os.environ.get('PUSH_KEY')
    print(f"--- 调试信息：检测到的 PUSH_KEY 长度为 {len(token) if token else 0} ---")
    if not token:
        print("错误：未从环境变量中获取到 PUSH_KEY")
        return

    url = 'http://www.pushplus.plus/send'
    payload = {"token": token, "title": "🤖 今日 AI 论文速递", "content": msg, "template": "markdown"}
    res = requests.post(url, json=payload)
    print(f"--- 调试信息：pushplus 返回结果：{res.text} ---")

if __name__ == "__main__":
    # 简化测试：先不抓论文，直接发一段话看能不能收到
    test_msg = "机器人重新出发！如果你看到这条消息，说明 GitHub 终于把钥匙传给 pushplus 了。"
    send_to_wechat(test_msg)
