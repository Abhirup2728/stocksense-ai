"""
vector_tool.py
Semantic search over company news using FAISS + sentence embeddings.
Loads the embedding model once at import time for efficiency.
"""

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_core.tools import tool

from tools.news_tool import fetch_news


EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

_embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)


def vector_search(company_name: str, query: str, k: int = 3) -> dict:
    """
    Fetches news for a company, builds a FAISS index of the articles,
    and returns the top-k articles most semantically relevant to the query.
    """
    news_result = fetch_news(company_name)

    if "error" in news_result:
        return news_result

    articles = news_result["articles"]

    if not articles:
        return {
            "company_name": company_name,
            "query": query,
            "results": [],
        }

    texts = [a["title"] + ". " + a.get("description", "") for a in articles]

    embeddings = _embedding_model.encode(texts, convert_to_numpy=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    query_embedding = _embedding_model.encode([query], convert_to_numpy=True)
    k = min(k, len(articles))
    distances, indices = index.search(query_embedding, k)

    results = []
    for rank, idx in enumerate(indices[0]):
        results.append({
            "title": articles[idx]["title"],
            "description": articles[idx].get("description", ""),
            "source": articles[idx]["source"],
            "relevance_distance": round(float(distances[0][rank]), 4),
        })

    return {
        "company_name": company_name,
        "query": query,
        "results": results,
    }


@tool
def vector_search_tool(company_name: str, query: str) -> dict:
    """
    Searches recent news about a company for content semantically
    relevant to a specific question, using vector similarity search.

    Use this tool when you need to find news related to a SPECIFIC
    aspect of the company (e.g. "growth plans", "regulatory issues",
    "management changes") rather than just the latest headlines.

    Args:
        company_name: The name of the company (e.g. "Reliance Industries").
        query: The specific topic or question to search for
               (e.g. "growth plans and business expansion",
               "regulatory or legal challenges",
               "management changes or leadership news").

    Returns:
        A dictionary with the top 3 most relevant articles, including
        title, description, source, and relevance score.
    """
    return vector_search(company_name, query, k=3)
