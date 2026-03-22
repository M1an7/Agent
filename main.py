from dotenv import load_dotenv
load_dotenv() 
import os
from agent.research_agent import ResearchAgent
from agent.rag_agent import RagAgent
import argparse
# 搜索agent入口
def run_web_search():
    question = input("Enter Your research question: ").strip()
    agent = ResearchAgent()
    report = agent.run(question)    # agent启动生成回复并打印
    print("\n"+report)

# 传文档接口
def run_pdf_ingest(pdf_path:str):
    rag = RagAgent()
    msg = rag.ingest_pdf(pdf_path)
    print(msg)

# 
def run_pdf_qa():
    question = input("Enter Your research question: ").strip()
    rag = RagAgent()
    ans = rag.ask(question)
    print("\n"+ans)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("web_search",help="Run web research agent")

    p_ingest = sub.add_parser("pdf_ingest")
    p_ingest.add_argument("pdf_path", help="Path to the PDF file")

    p_qa=sub.add_parser("pdf_qa")
    p_qa.add_argument("--question", help= "Your question about the ingested PDF")

    args = parser.parse_args()
    if args.cmd is None or args.cmd == "web_search":
        run_web_search()
    elif args.cmd == "pdf_ingest":
        run_pdf_ingest(args.pdf_path)
    elif args.cmd == "pdf_qa":
        run_pdf_qa()
    else:
        parser.print_help()    

if __name__ == "__main__":
    main()