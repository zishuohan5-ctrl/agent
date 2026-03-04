import os
import requests
from huggingface_hub import HfApi

def get_hf_papers():
    # 抓取 Hugging Face 每日热门论文
    try:
        api = HfApi()
        papers = api.get_daily_papers()
        # 只取前5篇，避免文字太长
        return [{"title": p.title, "url": f"https://huggingface.co/papers/{p.id}"} for p in papers[:5]]
    except Exception as e:
        print(f"获取论文失败: {e}")
        return []

def ask_ai(content):
    # 让 DeepSeek 大脑进行总结
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key: return "未检测到 DeepSeek API Key，请检查 GitHub Secrets 设置。"
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = f"你是一个AI科研助手。请将以下论文标题翻译成中文，并用一句话概括其核心创新点：\n{content}"
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    try:
        res = requests.post(url, json=data, headers=headers).json()
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 总结出错啦: {str(e)}"

def send_to_wechat(msg):
    # 这是你刚才截图里的 pushplus 发送逻辑
    token = os.environ.get('PUSH_KEY') 
    if not token: 
        print("未检测到 PUSH_KEY")
        return
        
    url = 'http://www.pushplus.plus/send'
    payload = {
        "token": token,
        "title": "🤖 今日 AI 论文速递",
        "content": msg,
        "template": "markdown" # 使用 markdown 格式让微信阅读更整洁
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    # 1. 获取数据
    papers = get_hf_papers()
    if papers:
        raw_text = "\n".join([f"- {p['title']} (链接: {p['url']})" for p in papers])
        # 2. AI 总结
        summary = ask_ai(raw_text)
        # 3. 推送微信
        send_to_wechat(summary)
        print("任务完成，消息已寄出！")
    else:
        print("今天没有更新论文。")
