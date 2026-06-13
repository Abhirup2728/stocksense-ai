# 📊 StockSense AI — Autonomous Financial Research Agent

An AI agent that performs end-to-end equity research on any NSE/BSE-listed Indian company. Give it a company name, and it autonomously fetches live financial data, analyzes recent news sentiment, retrieves contextually relevant articles via semantic search, and generates a structured analyst-style report — in under 30 seconds.

**🔗 Live Demo:** [stocksense-ai.streamlit.app](https://stocksense-ai.streamlit.app) *(coming soon)*

---

## 🎯 What It Does

Type a company name (e.g. *"Reliance Industries"*) and the agent will:

1. **Fetch live financial data** — current price, market cap, PE ratio, EPS, 52-week range, dividend yield, beta, 3-month momentum, and analyst recommendation (via `yfinance`)
2. **Analyze news sentiment** — pulls recent headlines (via NewsAPI) and scores each one using **FinBERT**, a finance-specific NLP model, producing a composite sentiment score
3. **Semantic search over news** — embeds articles with sentence-transformers and uses **FAISS** to retrieve the most relevant articles for specific themes (growth opportunities vs. risks)
4. **Synthesize a structured report** — an LLM (LLaMA 3 via Groq) autonomously orchestrates all of the above using **LangChain tool-calling agents**, then writes a structured report with Company Overview, Financial Snapshot, Sentiment Analysis, Growth Opportunities, Risks & Challenges, and an Analyst Summary

---

## 🏗️ Architecture
