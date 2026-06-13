"""
news_tool.py
Fetches and filters recent news articles for a company using NewsAPI.
"""

import os
from newsapi import NewsApiClient
from langchain_core.tools import tool


def fetch_news(company_name: str, max_articles: int = 10) -> dict:
    """
    Fetches recent, relevant news articles about a company.
    Filters out articles that don't actually mention the company.
    """
    try:
        newsapi = NewsApiClient(api_key=os.environ["NEWSAPI_KEY"])

        query = '"' + company_name + '"'

        response = newsapi.get_everything(
            q=query,
            language="en",
            sort_by="publishedAt",
            page_size=max_articles * 2
        )

        if response["status"] != "ok":
            return {"error": "NewsAPI returned status: " + response["status"]}

        articles = []
        seen_titles = set()
        key_term = company_name.split()[0].lower()

        for article in response["articles"]:
            title = article.get("title")
            description = article.get("description") or ""

            if not title or title == "[Removed]":
                continue
            if title in seen_titles:
                continue

            combined_text = (title + " " + description).lower()
            if key_term not in combined_text:
                continue

            seen_titles.add(title)

            articles.append({
                "title": title,
                "description": description,
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", ""),
                "url": article.get("url", ""),
            })

            if len(articles) >= max_articles:
                break

        return {
            "company_name": company_name,
            "article_count": len(articles),
            "articles": articles,
        }

    except Exception as e:
        return {"error": "Failed to fetch news for '" + company_name + "': " + str(e)}


@tool
def fetch_news_tool(company_name: str) -> dict:
    """
    Fetches recent news headlines and descriptions about a company.

    Use this tool when you need the latest news, announcements, deals,
    or developments related to a company to assess sentiment or context.

    Args:
        company_name: The name of the company (e.g. "Reliance Industries",
                       "Tata Consultancy Services", "HDFC Bank").

    Returns:
        A dictionary containing a list of recent articles with title,
        description, source, published date, and URL.
    """
    return fetch_news(company_name)
