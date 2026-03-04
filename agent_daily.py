import os
import requests
from huggingface_hub import list_papers
from datetime import datetime, timedelta

def get_specialized_papers():
    """精准抓取 Agent, RL, LLM 领域的论文"""
    # 定义你关心的关键词
    keywords = ["Agent", "Reinforcement Learning", "LLM"]
    results = []
    seen_ids = set()
    
    print(f"正在抓取领域相关论文: {keywords}...")
    
    try:
        for word in keywords:
            # 使用 search 参数解决接口报错
            # 这里的 search 会过滤出包含关键词的最新论文
            papers = list_papers(search=word)
            
            count = 0
            for p in papers:
                if count >= 3: break # 每个领域抓前 3 篇，避免消息太长
                if p.id not in seen_ids:
                    results.append({
                        "domain": word,
                        "title": p.title,
                        "url": f"https://huggingface.co/papers/{p.id}"
                    })
                    seen_ids.add(p.id)
                    count += 1
        return results
    except Exception as e:
        print(f"获取论文失败: {e}")
        return []

def ask_ai(content):
    """调用 DeepSeek 进行专业总结"""
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = (
        "你是一个顶级的 AI 研究助手。请针对以下提供的 Agent、RL、LLM 领域的论文列表，"
        "将其标题翻译成中文，并用一句话说明该论文对该领域的研究者有什么启发。"
        "要求：内容要硬核，不要套话。\n\n"
        f"论文列表如下：\n{content}"
    )
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    try:
        res = requests.post(url, json=data, headers=headers).json()
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 总结出错: {str(e)}"

def send_to_wechat(msg):
    """发送到微信"""
    token = os.environ.get('PUSH_KEY')
    url = 'http://www.pushplus.plus/send'
    payload = {
        "token": token, 
        "title": "🎯 定制 AI 论文速递 (Agent/RL/LLM)", 
        "content": msg, 
        "template": "markdown"
    }
    res = requests.post(url, json=payload)
    print(f"Pushplus 反馈: {res.text}")

if __name__ == "__main__":
    # 1. 获取指定领域的论文
    papers = get_specialized_papers()
    
    if papers:
        # 2. 格式化给 AI
        raw_text = ""
        for p in papers:
            raw_text += f"领域 [{p['domain']}]: {p['title']} (原文: {p['url']})\n"
        
        print("正在进行深度总结...")
        # 3. AI 总结
        summary = ask_ai(raw_text)
        
        # 4. 推送
        send_to_wechat(summary)
        print("任务完成！")
    else:
        print("今日未找到相关领域的更新。")
