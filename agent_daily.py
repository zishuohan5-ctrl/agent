import os
import requests
from huggingface_hub import list_papers

def get_hf_papers():
    """获取 Hugging Face 每日热门论文 (修复后的新版方法)"""
    try:
        print("正在从 Hugging Face 获取论文列表...")
        # 使用新版 list_papers 方法
        papers = list_papers(sort="daily_papers")
        
        results = []
        for i, p in enumerate(papers):
            if i >= 5: break  # 只取前 5 篇，避免消息过长
            results.append({
                "title": p.title, 
                "url": f"https://huggingface.co/papers/{p.id}"
            })
        return results
    except Exception as e:
        print(f"获取论文失败: {e}")
        return []

def ask_ai(content):
    """调用 DeepSeek 进行翻译和总结"""
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        return "错误：未检测到 DEEPSEEK_API_KEY，请检查 GitHub Secrets 设置。"
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}", 
        "Content-Type": "application/json"
    }
    
    prompt = (
        "你是一个专业的 AI 科研助手。请将以下论文标题翻译成中文，"
        "并用通俗易懂的一句话概括其核心创新点。格式如下：\n"
        "1. [中文标题]\n概括：xxx\n\n"
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
        "title": "🤖 今日 AI 论文速递",
        "content": msg,
        "template": "markdown"
    }
    
    try:
        res = requests.post(url, json=payload)
        print(f"Pushplus 发送反馈: {res.text}")
    except Exception as e:
        print(f"发送微信失败: {e}")

if __name__ == "__main__":
    # 1. 抓取论文
    papers_list = get_hf_papers()
    
    if papers_list:
        # 2. 整理原始文本
        raw_text = ""
        for p in papers_list:
            raw_text += f"- {p['title']} (原文链接: {p['url']})\n"
        
        print(f"成功获取 {len(papers_list)} 篇论文，正在请求 AI 总结...")
        
        # 3. AI 总结
        final_summary = ask_ai(raw_text)
        
        # 4. 推送到微信
        send_to_wechat(final_summary)
        print("所有任务已完成！")
    else:
        print("未能获取到今日论文，任务终止。")
