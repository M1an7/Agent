import os
from tqdm import tqdm
from tools.search_serper import serper_search
from tools.fetch_page import fetch_html
from tools.extract_text import extract_main_text
from agent.prompts import PLAN_PROMPT, SYNTH_PROMPT
from openai import OpenAI


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE_URL","https://api.openai.com/v1"),
    )
MODEL = os.getenv("LLM_MODEL","sherry_server")


class ResearchAgent:
    def plan_queries(self, question: str):
        prompt = PLAN_PROMPT.format(question=question)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"user","content":prompt}],
            temperature=0.3,
        )

        text = resp.choices[0].message.content
        queries = self.safe_parse_list(text)
        return queries[:1]
    
    def safe_parse_list(self, text: str):   #一个过滤函数
        lines = [l.strip("- ").strip() for l in text.splitlines() if l.strip()]
        return [l for l in lines if len(l)>3]

    def format_sources(self,sources):
        out = []
        for i,s in enumerate(sources):
            out.append(
                f"[{i+1}] {s['title']}\nURL: {s['link']}\nContent:{s['content']}\n"
            )
        return "\n".join(out)
        
    def format_source_list(self,sources):
        out = ["## Sources"]
        for i,s in enumerate(sources):
            out.append(f"[{i+1}]{s['title']}-{s['link']}")
        return "\n".join(out)
    
    def run(self, question: str):
        queries = self.plan_queries(question)   #搜索查询列表，输入question，生成查询来回答，返回的是查询

        sources = []
        for q in tqdm(queries, desc="Searching"):
            sources += serper_search(q,k=1)  #对每个查询进行搜索，返回搜索结果列表

        seen = set()
   
        
        sources = [s for s in sources if not (s["link"]) in seen or seen.add(s["link"])]  #去重
        input(f"{sources}")
        
        enriched = []
        for s in tqdm(sources[:8], desc="Fetching pages"):
            html = fetch_html(s["link"])
            if not html:
                continue
            text = extract_main_text(html)
            if text and len(text)>300:
                enriched.append({
                    "title": s["title"],
                    "link": s["link"],
                    "snippet": s["snippet"],
                    "text": text[:4000]   #截断文本，防止过长
                })

        prompt = SYNTH_PROMPT.format(question=question,sources=self.format_sources(enriched))
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"user","content":prompt}],
            temperature=0.2
        ) 
        return resp.choices[0].message.content+"\n\n"+self.format_source_list(enriched)