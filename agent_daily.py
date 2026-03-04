import os
import requests
from huggingface_hub import list_papers

def get_hf_papers():
    """获取 Hugging Face 论文列表（兼容性最强版本）"""
    try:
        print("正在从 Hugging Face 获取最新论文列表...")
        # 移除了所有可能导致版本冲突的参数
        papers = list_papers()
        
        results = []
        count = 0
        for p in papers:
            if count >= 5: break  # 选取前 5 篇
            results.append({
                "title": p.title, 
                "url": f"https://huggingface.co/papers/{p.id}"
            })
            count += 1
        return results
    except Exception as e:
        print(f"获取论文失败: {e}")
        return []

def ask_ai(content):
    """调用 DeepSeek 对昨日论文进行总结"""
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        return "错误：未检测到 DEEPSEEK_API_KEY。"
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}", 
        "Content-Type": "application/json"
    }
    
    # 提示词已更新，专注于总结昨日论文
    prompt = (
        "你是一个专业的 AI 科研助手。请针对以下提供的【昨日】Hugging Face 热门论文列表，"
        "将其标题翻译成中文，并用通俗易懂的一句话概括每篇论文的核心创新点。"
        "格式要求：\n1. [中文标题]\n   创新点：xxx\n\n"
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
    """通过 pushplus 发送到微信"""
    token = os.environ.get('PUSH_KEY')
    if not token:
        print("错误：未检测到 PUSH_KEY")
        return

    url = 'http://www.pushplus.plus/send'
    payload = {
        "token": token,
        "title": "🤖 昨日 AI 论文精选总结",
        "content": msg,
        "template": "markdown"
    }
    
    try:
        res = requests.post(url, json=payload)
        print(f"Pushplus 发送反馈: {res.text}")
    except Exception as e:
        print(f"发送微信失败: {e}")

if __name__ == "__main__":
    # 1. 获取论文
    papers_list = get_hf_papers()
    
    if papers_list:
        raw_text = ""
        for p in papers_list:
            raw_text += f"- {p['title']} (原文链接: {p['url']})\n"
        
        print(f"成功获取 {len(papers_list)} 篇论文，正在请求 DeepSeek 进行昨日论文总结...")
        
        # 2. AI 总结
        final_summary = ask_ai(raw_text)
        
        # 3. 推送到微信
        send_to_wechat(final_summary)
        print("所有任务已完成！")
    else:
        print("未能获取到论文数据，请检查网络或库设置。")
