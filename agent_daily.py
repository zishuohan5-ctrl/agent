import os
import requests
from datetime import datetime, timedelta

def get_specialized_papers():
    """使用最原始的 API 请求方式，绕过库版本问题"""
    # 定义搜索关键词
    queries = ["Agent", "Reinforcement", "LLM"]
    results = []
    seen_ids = set()
    
    print(f"正在通过 API 检索领域论文: {queries}...")
    
    for q in queries:
        try:
            # 直接访问 Hugging Face 的 API 接口
            url = f"https://huggingface.co/api/papers?search={q}"
            response = requests.get(url, timeout=15)
            papers = response.json()
            
            count = 0
            for p in papers:
                if count >= 3: break  # 每个领域取前 3 篇
                paper_id = p.get('id')
                if paper_id and paper_id not in seen_ids:
                    results.append({
                        "domain": q,
                        "title": p.get('title', 'No Title'),
                        "url": f"https://huggingface.co/papers/{paper_id}"
                    })
                    seen_ids.add(paper_id)
                    count += 1
        except Exception as e:
            print(f"抓取关键词 {q} 失败: {e}")
            
    return results

def ask_ai(content):
    """调用 DeepSeek 进行硬核总结"""
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key: return "未检测到 API Key"
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = (
        "你是一个顶级的 AI 研究助手。请针对以下提供的 Agent、RL、LLM 领域的论文列表，"
        "将其标题翻译成中文，并用一句话说明该论文对该领域的研究者有什么启发。\n\n"
        f"论文列表：\n{content}"
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
    """通过 pushplus 发送"""
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
    papers = get_specialized_papers()
    if papers:
        raw_text = ""
        for p in papers:
            raw_text += f"[{p['domain']}] {p['title']}\n链接: {p['url']}\n"
        
        print(f"成功获取 {len(papers)} 篇论文，正在请求 AI 总结...")
        summary = ask_ai(raw_text)
        send_to_wechat(summary)
        print("所有流程已完成！")
    else:
        print("今日未找到相关更新。")
