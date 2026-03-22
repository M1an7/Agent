# sherry_agent（MVP）使用说明

这是一个轻量级 Agent 项目，包含两类能力：

- Web Research：自动生成检索词，抓取网页并汇总成结构化回答
- PDF RAG：导入 PDF 建立向量索引，基于检索片段回答问题

适合做原型验证：流程短、结构清晰、便于二次改造。

## 目录结构（核心）

- `main.py`：命令行入口
- `agent/research_agent.py`：联网检索与回答生成
- `agent/rag_agent.py`：PDF 入库与问答
- `tools/search_serper.py`：调用 Serper 搜索
- `tools/fetch_page.py`：抓取网页 HTML
- `tools/extract_text.py`：提取网页正文
- `tools/embedder.py`：调用 embedding 接口
- `tools/faiss_store.py`：FAISS 向量库读写与检索
- `tools/pdf_loader.py`：读取 PDF 文本
- `utils/chunker.py`：文本分块
- `run_vllm_embedding_api.sh`：本地 embedding 服务启动脚本（vLLM）

## 运行环境

- Python 3.9+
- Linux / macOS（Windows 建议用 WSL）

安装依赖：

```bash
pip install -r requirement.txt
# 如果出现 faiss 安装问题，可尝试
pip install faiss-cpu
```

## 环境变量

项目通过 `.env` 读取配置（代码里已调用 `load_dotenv()`）。

建议新建 `.env`：

```env
# LLM（OpenAI 兼容）
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE_URL=https://api.openai.com/v1
LLM_MODEL=sherry_server

# Web Search
SERPER_API_KEY=your_serper_api_key

# Embedding（OpenAI 兼容）
OPENAI_API_EMBED_URL=http://127.0.0.1:8666/v1
EMBED_MODEL=text2vec-base-chinese

# RAG 参数
RAG_INDEX_DIR=data/index
RAG_TOP_K=5
RAG_CHUNK_SIZE=1200
RAG_CHUNK_OVERLAP=200
```

说明：

- `OPENAI_API_BASE_URL` 和 `OPENAI_API_EMBED_URL` 可以指向同一服务，也可以分开
- 如果你使用本地 vLLM 提供 embedding，只需要保证 `OPENAI_API_EMBED_URL` 与 `EMBED_MODEL` 对应即可

## 快速开始

### 1) 联网检索问答

```bash
python main.py web_search
```

程序会提示输入问题，随后自动完成：

- 生成检索 query
- 调用 Serper 搜索
- 抓取网页并抽取正文
- 汇总答案并附来源

### 2) 导入 PDF（建立索引）

```bash
python main.py pdf_ingest /path/to/your.pdf
```

导入完成后，向量索引默认写入 `data/index`。

### 3) 基于 PDF 问答

```bash
python main.py pdf_qa
```

输入问题后，程序会：

- 从 FAISS 检索相关 chunk
- 拼接上下文
- 调用 LLM 生成答案（并附页码引用）

## 本地启动 embedding 服务（可选）

如果不想走远程 embedding API，可使用项目提供的脚本：

```bash
chmod +x run_vllm_embedding_api.sh
MODEL_PATH="/path/to/local/embedding-model" ./run_vllm_embedding_api.sh
```

默认端口是 `8666`，对应 `.env` 中：

```env
OPENAI_API_EMBED_URL=http://127.0.0.1:8666/v1
```

## 常见问题

1. `SERPER_API_KEY` 未配置

现象：联网搜索阶段报 401 或请求失败。  
处理：确认 `.env` 已配置，且 key 可用。

2. PDF 导入后无法问答

现象：索引文件缺失或检索为空。  
处理：先执行 `pdf_ingest`，确认 `data/index` 下存在 `index.faiss`、`metas.pkl`、`texts.pkl`。

3. 扫描版 PDF 提取不到文本

现象：导入时报 “No text extracted from PDF”。  
处理：先做 OCR，再导入。

4. FAISS 安装失败

现象：`import faiss` 报错。  
处理：优先安装 `faiss-cpu`，并确认 Python 版本与平台兼容。

## 已知注意点

当前代码中保留了两处调试输入，会在运行时阻塞：

- `agent/research_agent.py` 中 `input(f"{sources}")`
- `tools/faiss_store.py` 中 `input("debuging")`

如果你希望流程全自动，建议先移除或注释这两处。

