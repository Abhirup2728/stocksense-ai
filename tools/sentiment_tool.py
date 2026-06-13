"""
sentiment_tool.py
Analyzes financial news sentiment using FinBERT.
Loads the model once at import time for efficiency.
"""

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langchain_core.tools import tool

from tools.news_tool import fetch_news


MODEL_NAME = "ProsusAI/finbert"

_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
_model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = _model.to(_device)
_model.eval()


def score_sentiment(text: str) -> dict:
    """
    Returns sentiment label and confidence scores for a piece of text.
    """
    inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(_device)

    with torch.no_grad():
        outputs = _model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)[0]

    scores = {_model.config.id2label[i]: round(probs[i].item(), 4) for i in range(len(probs))}
    label = max(scores, key=scores.get)

    return {"label": label, "scores": scores}


def analyze_sentiment(articles: list) -> dict:
    """
    Takes a list of article dicts and returns per-article sentiment
    plus a composite score from -1 (very negative) to +1 (very positive).
    """
    if not articles:
        return {
            "composite_score": 0.0,
            "overall_sentiment": "neutral",
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "article_sentiments": [],
        }

    article_sentiments = []
    score_sum = 0.0

    for article in articles:
        text = article["title"]
        if article.get("description"):
            text += ". " + article["description"]

        result = score_sentiment(text)
        label = result["label"]
        scores = result["scores"]

        signed_score = round(scores["positive"] - scores["negative"], 4)
        score_sum += signed_score

        article_sentiments.append({
            "title": article["title"],
            "sentiment": label,
            "signed_score": signed_score,
        })

    composite_score = round(score_sum / len(articles), 4)

    if composite_score > 0.15:
        overall = "positive"
    elif composite_score < -0.15:
        overall = "negative"
    else:
        overall = "neutral"

    positive_count = sum(1 for a in article_sentiments if a["sentiment"] == "positive")
    negative_count = sum(1 for a in article_sentiments if a["sentiment"] == "negative")
    neutral_count = sum(1 for a in article_sentiments if a["sentiment"] == "neutral")

    return {
        "composite_score": composite_score,
        "overall_sentiment": overall,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "article_sentiments": article_sentiments,
    }


@tool
def sentiment_analysis_tool(company_name: str) -> dict:
    """
    Fetches recent news for a company and analyzes the sentiment
    of each headline using FinBERT (a finance-specific NLP model).

    Use this tool to gauge market sentiment and news tone for a company
    before forming an investment view.

    Args:
        company_name: The name of the company (e.g. "Reliance Industries",
                       "Tata Consultancy Services", "HDFC Bank").

    Returns:
        A dictionary with a composite sentiment score (-1 to +1),
        an overall sentiment label, sentiment counts, and per-article
        sentiment breakdown.
    """
    news_result = fetch_news(company_name)

    if "error" in news_result:
        return news_result

    return analyze_sentiment(news_result["articles"])
