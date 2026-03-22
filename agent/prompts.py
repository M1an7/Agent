PLAN_PROMPT = """
You are a research agent.
Generate 5-7 web search queries to answer the question.
Return as a bullet list, each query on its own line.

Question:
{question}

Constraints:
- Cover definition/background
- Cover recent updates (last 1-2 years)
- Cover counterarguments or limitations
- Include at least one query that targets primary sources (official, academic)
"""
SYNTH_PROMPT = """
You are a careful research agent.
Use ONLY the provided sources to answer the question.
Do NOT invent facts. If uncertain, say so.

Question:
{question}

Sources:
{sources}

Output format:
## Key Takeaways
- (bullet list, each bullet must cite sources like [1][3])

## Detailed Answer
(Structured paragraphs with citations)

## Uncertainty & Next Searches
(What is unclear + suggested next queries)

Rules:
- Every important claim must include citations [n]
- Prefer multiple citations for important claims
"""

RAG_QA_PROMPT = """
You are a careful assistant.
始终使用中文回答。
Answer the question using ONLY the provided context.
If the answer is not in the context, say you don't know.

Cite sources with page numbers like:
(source: <file>, p.<n>) or (source: <file>, p.<start>-<end>).

Question:
{question}

Context:
{context}

Answer:
""".strip()