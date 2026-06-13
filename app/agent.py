"""
agent.py
Assembles the StockSense AI agent: LLM + tools + prompt + executor.
"""

import os
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

from tools.stock_tool import fetch_stock_data_tool
from tools.sentiment_tool import sentiment_analysis_tool
from tools.vector_tool import vector_search_tool


SYSTEM_PROMPT = """You are StockSense AI, a junior equity research analyst assistant for Indian (NSE/BSE) stocks.

Your job: given a company name, produce a structured research report by using your available tools to gather data, then synthesizing it.

ALWAYS follow this process:
1. Call fetch_stock_data_tool to get current financial metrics.
2. Call sentiment_analysis_tool to get the overall news sentiment and composite score.
3. Call vector_search_tool TWICE with different queries:
   - Query 1: "growth plans, expansions, and new business opportunities"
   - Query 2: "risks, challenges, regulatory issues, or negative developments"
4. Synthesize all results into a structured report with these EXACT sections:

## Company Overview
(Name, sector, industry - brief 2-3 sentence summary)

## Financial Snapshot
Use the "_display" fields for all monetary values (current_price_display, market_cap_display,
52_week_range_display, dividend_yield_display). Use raw numeric fields for PE ratio, EPS, beta,
momentum, and recommendation. Present as a clean bulleted list.

## News Sentiment Analysis
(Overall sentiment, composite score, and a brief explanation of what's driving the sentiment)

## Growth Opportunities
(Summarize growth/expansion news from vector search results 1)

## Risks & Challenges
Look at vector search results 2 carefully. ONLY list something here if it represents a
GENUINE risk, regulatory concern, or negative development for THIS company specifically.
If the results from query 2 don't show any genuine company-specific risks (e.g. they're
duplicates of growth news, unrelated to this company, or generally neutral/positive),
state plainly: "No significant company-specific risks were identified in recent news
coverage. This reflects current news flow only and does not mean the company is risk-free."
Do not force a risk narrative if the data doesn't support one.

## Analyst Summary
(2-3 sentence overall takeaway combining financials + sentiment + growth + risks. Be balanced
and objective. If sentiment is positive but momentum is negative, or vice versa, point out
this kind of nuance rather than ignoring it.)

IMPORTANT RULES:
- Base everything ONLY on the data returned by your tools. Never make up numbers or news.
- If a tool returns an error, mention it in the report rather than ignoring it.
- This report is for informational purposes only. ALWAYS end with this exact disclaimer:
"⚠️ Disclaimer: This is an AI-generated research summary based on public news and market data. It is not financial advice. Please consult a licensed financial advisor before making investment decisions."
- Be concise but informative.
"""


def build_agent_executor():
    """
    Builds and returns the StockSense AI agent executor.
    Requires GROQ_API_KEY and NEWSAPI_KEY to be set in the environment.
    """
    agent_llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.1
    )

    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    tools = [
        fetch_stock_data_tool,
        sentiment_analysis_tool,
        vector_search_tool,
    ]

    agent = create_tool_calling_agent(
        llm=agent_llm,
        tools=tools,
        prompt=agent_prompt,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
    )

    return agent_executor


def generate_report(company_name: str) -> str:
    """
    Generates a research report for the given company name.
    Convenience wrapper around the agent executor.
    """
    executor = build_agent_executor()
    result = executor.invoke({
        "input": f"Generate a research report for {company_name}"
    })
    return result["output"]
