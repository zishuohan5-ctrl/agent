import os
import requests
import xml.etree.ElementTree as ET

def get_arxiv_papers():
    """从 arXiv 抓取 Agent, RL, LLM 领域的最新论文"""
    # 定义搜索关键词：智能体、强化学习、大语言模型
    # cs.AI 是人工智能分类，cs.LG 是机器学习分类
    queries = [
        'all:Agent', 
        'all:"Reinforcement Learning"', 
        'all:LLM'
    ]
    
    results = []
    seen_titles = set()
    print("正在连接 arXiv 服务器检索最新论文...")

    for q in queries:
        try:
            # arXiv API URL: 每次取最新上传的 3 篇
            url = f'http://export.arxiv.org/api/query?search_query={q}&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending'
            response = requests.get(url, timeout=15)
            
            # 解析 arXiv 返回的 XML 数据
            root = ET.fromstring(response.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                link = entry.find('atom:id', ns).text
                
                if title not in seen_titles:
                    results.append({
                        "domain": q.replace('all:', '').replace('"', ''),
                        "title": title,
                        "url": link
                    })
                    seen_titles.add(title)
        except Exception as e:
            print(f"搜索 {q} 失败: {e}")
            
    return results

def ask_ai(content):
    """调用 DeepSeek 总结"""
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key: return "未检测到 API Key"
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = (
        "你是一个顶级的 AI 研究专家。请针对以下提供的 arXiv 最新论文列表，"
        "将其标题翻译成中文，并用一句话说明该论文对 Agent、RL 或 LLM 领域的研究者有什么核心价值。\n\n"
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
    """通过 pushplus 发送到微信"""
    token = os.environ.get('PUSH_KEY')
    url = 'http://www.pushplus.plus/send'
    payload = {
        "token": token, 
        "title": "🎯 arXiv 定制速递 (Agent/RL/LLM)", 
        "content": msg, 
        "template": "markdown"
    }
    res = requests.post(url, json=payload)
    print(f"Pushplus 反馈: {res.text}")

if __name__ == "__main__":
    # 1. 抓取论文
    papers = get_arxiv_papers()
    
    if papers:
        raw_text = ""
        for p in papers:
            raw_text += f"[{p['domain']}] {p['title']}\n链接: {p['url']}\n"
        
        print(f"成功获取 {len(papers)} 篇最新 arXiv 论文，正在请求总结...")
        # 2. 总结并发送
        summary = ask_ai(raw_text)
        send_to_wechat(summary)
        print("所有流程已完成！")
    else:
        print("未能在 arXiv 找到相关论文更新。")
