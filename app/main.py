"""
main.py
StockSense AI - Premium Streamlit frontend.
"""

import streamlit as st
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import generate_report


# ----------------------------------------------------------------
# Page config
# ----------------------------------------------------------------
st.set_page_config(
    page_title="StockSense AI",
    page_icon="\U0001F4CA",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ----------------------------------------------------------------
# Custom CSS - dark glassmorphic theme
# ----------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Hide default Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Overall background */
    .stApp {
        background-color: #0A0F1C;
    }

    /* Constrain and center content */
    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        margin: 0 auto;
    }

    /* Typography */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
    }

    /* Top nav bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0 1.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 2rem;
    }
    .top-nav-logo {
        font-size: 1.4rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .top-nav-links {
        display: flex;
        gap: 1.8rem;
    }
    .top-nav-links a {
        color: #9CA3AF;
        text-decoration: none;
        font-size: 0.9rem;
        transition: color 0.2s;
    }
    .top-nav-links a:hover {
        color: #FFFFFF;
    }

    /* Hero */
    .hero-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }
    .hero-subtitle {
        text-align: center;
        color: #9CA3AF;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    /* Glassmorphic search container */
    .search-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 1.8rem 2rem;
        border: 1px solid transparent;
        background-image: linear-gradient(rgba(255,255,255,0.03), rgba(255,255,255,0.03)),
                           linear-gradient(120deg, rgba(189,176,139,0.6) 0%, rgba(0,102,255,0.35) 100%);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        margin-bottom: 1.5rem;
    }
    .search-label {
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        color: #BDB08B;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    .search-helper {
        text-align: center;
        color: #6B7280;
        font-size: 0.82rem;
        margin-top: 0.6rem;
    }

    /* Text input override */
    .stTextInput input {
        background-color: #11182B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
        padding: 0.7rem 1rem !important;
        font-size: 0.95rem !important;
    }
    .stTextInput input::placeholder {
        color: #6B7280 !important;
    }
    .stTextInput input:focus {
        border-color: #0066FF !important;
        box-shadow: 0 0 0 1px #0066FF !important;
    }

    /* Button override */
    .stButton button {
        background: linear-gradient(90deg, #0066FF, #3385FF) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.7rem 2.5rem !important;
        box-shadow: 0 0 15px rgba(0, 102, 255, 0.5) !important;
        transition: box-shadow 0.2s, transform 0.1s !important;
        width: 100% !important;
    }
    .stButton button:hover {
        box-shadow: 0 0 25px rgba(0, 102, 255, 0.8) !important;
        transform: translateY(-1px);
    }

    /* Download button override (secondary style) */
    .stDownloadButton button {
        background: rgba(255,255,255,0.05) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        width: 100% !important;
    }
    .stDownloadButton button:hover {
        border-color: #0066FF !important;
        color: #0066FF !important;
    }

    /* Agent flow row */
    .agent-flow-label {
        text-align: center;
        color: #6B7280;
        font-size: 0.85rem;
        margin: 1.5rem 0 0.8rem 0;
    }
    .agent-flow-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-bottom: 2.5rem;
    }
    .agent-flow-step {
        color: #9CA3AF;
        font-size: 0.85rem;
        white-space: nowrap;
    }
    .agent-flow-arrow {
        color: #4B5563;
    }

    /* Report container */
    .report-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.2rem;
    }
    .report-card h3 {
        color: #FFFFFF;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .report-card p, .report-card li {
        color: #D1D5DB;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    /* Sentiment badges */
    .sentiment-badge {
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    .sentiment-positive { background: rgba(16, 185, 129, 0.15); color: #10B981; }
    .sentiment-negative { background: rgba(239, 68, 68, 0.15); color: #EF4444; }
    .sentiment-neutral  { background: rgba(156, 163, 175, 0.15); color: #9CA3AF; }

    /* Financial metrics grid */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.8rem;
        margin-top: 0.5rem;
    }
    .metric-box {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 0.7rem 0.9rem;
    }
    .metric-label {
        color: #6B7280;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.2rem;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 1rem;
        font-weight: 700;
    }

    /* Disclaimer box */
    .disclaimer-box {
        background: rgba(239, 68, 68, 0.06);
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        color: #FCA5A5;
        font-size: 0.82rem;
        line-height: 1.5;
        margin-top: 1rem;
    }

    /* Footer */
    .footer-section {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(255,255,255,0.06);
    }
    .footer-title {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.6rem;
    }
    .footer-text {
        color: #6B7280;
        font-size: 0.82rem;
        line-height: 1.6;
    }
    .tech-pill-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    .tech-pill {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        color: #D1D5DB;
        font-size: 0.8rem;
        text-align: center;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------
# Top navigation
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="top-nav">
        <div class="top-nav-logo">\U0001F4C8 StockSense AI</div>
        <div class="top-nav-links">
            <a href="#">Watchlist</a>
            <a href="#">Reports History</a>
            <a href="#">API Docs</a>
            <a href="#">Account</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------
# Hero section
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="hero-title">Your On-Demand Junior Equity Analyst<br>for NSE/BSE Stocks</div>
    <div class="hero-subtitle">Instant automated research reports covering financials, sentiment, growth opportunities, and risks.</div>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------
# Search card
# ----------------------------------------------------------------
st.markdown('<div class="search-card">', unsafe_allow_html=True)
st.markdown('<div class="search-label">START YOUR RESEARCH</div>', unsafe_allow_html=True)

company_name = st.text_input(
    "Company name",
    placeholder="ENTER COMPANY NAME (NSE/BSE)",
    label_visibility="collapsed",
)

st.markdown(
    '<div class="search-helper">e.g., Reliance Industries, HDFC Bank, Infosys, Tata Motors</div>',
    unsafe_allow_html=True,
)

generate_clicked = st.button("GENERATE INSIGHTS REPORT", type="primary")

st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------
# Agent flow indicator
# ----------------------------------------------------------------
st.markdown('<div class="agent-flow-label">Powered by Autonomous AI Agents &amp; Tool Calling</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="agent-flow-row">
        <span class="agent-flow-step">\U0001F4C8 Fetch Financials</span>
        <span class="agent-flow-arrow">&rarr;</span>
        <span class="agent-flow-step">\U0001F4F0 Analyze News</span>
        <span class="agent-flow-arrow">&rarr;</span>
        <span class="agent-flow-step">\U0001F4AC Sentiment Scoring</span>
        <span class="agent-flow-arrow">&rarr;</span>
        <span class="agent-flow-step">\U0001F50D Vector Search</span>
        <span class="agent-flow-arrow">&rarr;</span>
        <span class="agent-flow-step">\U0001F4CB Structure Report</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------
# Generate and display report
# ----------------------------------------------------------------
if generate_clicked:
    if not company_name.strip():
        st.warning("Please enter a company name.")
    else:
        with st.spinner(f"Researching {company_name}... this may take 20-40 seconds"):
            try:
                report = generate_report(company_name)
                st.session_state["last_report"] = report
                st.session_state["last_company"] = company_name
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")


# ----------------------------------------------------------------
# Render stored report (persists across reruns)
# ----------------------------------------------------------------
if "last_report" in st.session_state:
    report = st.session_state["last_report"]
    company = st.session_state["last_company"]

    # Parse sections
    pattern = r"^##\s+(.+?)\s*$"
    lines = report.split("\n")
    sections = {}
    current_heading = None
    current_content = []
    for line in lines:
        match = re.match(pattern, line)
        if match:
            if current_heading:
                sections[current_heading] = "\n".join(current_content).strip()
            current_heading = match.group(1).strip()
            current_content = []
        else:
            current_content.append(line)
    if current_heading:
        sections[current_heading] = "\n".join(current_content).strip()

    st.markdown("---")
    st.markdown(f"## \U0001F4CA Research Report: {company}")

    # Render each section as a card
    icons = {
        "Company Overview": "\U0001F3E2",
        "Financial Snapshot": "\U0001F4B0",
        "News Sentiment Analysis": "\U0001F4F0",
        "Growth Opportunities": "\U0001F4C8",
        "Risks & Challenges": "\u26A0\uFE0F",
        "Analyst Summary": "\U0001F4DD",
    }

    for heading, content in sections.items():
        icon = icons.get(heading, "\U0001F4C4")

        # Strip disclaimer from Analyst Summary if present
        disclaimer_text = None
        if "Disclaimer" in content:
            parts = content.split("\u26A0\uFE0F")
            content = parts[0].strip()
            if len(parts) > 1:
                disclaimer_text = "\u26A0\uFE0F" + parts[1].strip()

        st.markdown(f'<div class="report-card"><h3>{icon} {heading}</h3>', unsafe_allow_html=True)

        if heading == "News Sentiment Analysis":
            sentiment_class = "sentiment-neutral"
            if "positive" in content.lower()[:200]:
                sentiment_class = "sentiment-positive"
            elif "negative" in content.lower()[:200]:
                sentiment_class = "sentiment-negative"
            badge_label = sentiment_class.replace("sentiment-", "").upper()
            st.markdown(f'<span class="sentiment-badge {sentiment_class}">{badge_label}</span>', unsafe_allow_html=True)

        st.markdown(content)

        if disclaimer_text:
            st.markdown(f'<div class="disclaimer-box">{disclaimer_text}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Download buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="\U0001F4C4 Download as Markdown",
            data=report,
            file_name=f"StockSense_AI_Report_{company.replace(' ', '_')}.md",
            mime="text/markdown",
        )


# ----------------------------------------------------------------
# Footer
# ----------------------------------------------------------------
st.markdown('<div class="footer-section">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.5, 2, 1.5], gap="large")

with col1:
    st.markdown('<div class="footer-title">About StockSense AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="footer-text">StockSense AI is an on-demand junior equity analyst for NSE/BSE stocks. '
        'It autonomously fetches financials, analyzes news sentiment, and identifies growth '
        'opportunities and risks using AI agents.</div>',
        unsafe_allow_html=True,
    )

with col2:
    st.markdown('<div class="footer-title">Tech Stack</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="tech-pill-grid">
            <div class="tech-pill">\U0001F517 LangChain Agents</div>
            <div class="tech-pill">\u26A1 Groq (LLaMA 3)</div>
            <div class="tech-pill">\U0001F4C8 yfinance</div>
            <div class="tech-pill">\U0001F9E0 FAISS Vector DB</div>
            <div class="tech-pill">\U0001F916 FinBERT NLP</div>
            <div class="tech-pill">\U0001F4BB Streamlit</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown('<div class="footer-title">NSE/BSE Info &amp; Disclaimers</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="footer-text">All data is sourced from public APIs (yfinance, NewsAPI) for '
        'educational and informational purposes only. This is NOT financial advice. '
        'Please consult a licensed financial advisor before making investment decisions.</div>',
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)
