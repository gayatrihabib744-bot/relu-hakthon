import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from google import genai
import time

st.set_page_config(page_title="Company Research Assistant", layout="wide")

API_KEY = "AQ.Ab8RN6IUk0ouq0A8TAmiM6w5D-m0S70nbvgutoCrRX90dpDuTA"
client = genai.Client(api_key=API_KEY)

def fetch_company_data(company_input):
    try:
        if not company_input.startswith("http"):
            company_input = "https://www." + company_input.replace(" ", "") + ".com"
        response = requests.get(company_input, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        texts = []
        for tag in soup.find_all(["p", "h1", "h2", "h3"])[:30]:
            text = tag.get_text(strip=True)
            if text:
                texts.append({"content": text})
        return pd.DataFrame(texts) if texts else pd.DataFrame(columns=["content"])
    except Exception as e:
        st.error(f"Failed to fetch: {e}")
        return pd.DataFrame(columns=["content"])

def ai_research(company_input, text):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=f"""You are a company research assistant. Based on this data from {company_input}, provide a structured research report with:
1. Company Overview
2. Products/Services
3. Key Facts
4. Summary

Data: {text[:3000]}"""
        )
        return response.text
    except Exception as e:
        return f"AI temporarily unavailable. Raw data collected successfully!\n\nData preview: {text[:500]}..."

def main():
    st.title("🏢 AI Company Research Assistant")
    st.caption("Enter a company name or website URL to get an AI-powered research report")

    with st.sidebar:
        st.header("🔍 Research Controls")
        company_input = st.text_input("Company name or URL", placeholder="e.g. Apple or https://apple.com")
        run_button = st.button("🚀 Research Company", type="primary")

    if run_button and company_input:
        with st.spinner("Fetching company data..."):
            df = fetch_company_data(company_input)

        if df.empty:
            st.warning("No data found. Try a different company name or URL.")
            st.stop()

        st.subheader("📥 Raw Data Collected")
        st.dataframe(df, use_container_width=True)

        with st.spinner("Generating AI research report..."):
            text = " ".join(df["content"].tolist())
            report = ai_research(company_input, text)

        st.subheader("🤖 AI Research Report")
        st.write(report)

        st.subheader("📊 Data Stats")
        col1, col2, col3 = st.columns(3)
        col1.metric("Data Points", len(df))
        col2.metric("Avg Length", int(df["content"].str.len().mean()))
        col3.metric("Analyzed at", time.strftime("%H:%M:%S"))

        df["length"] = df["content"].str.len()
        st.bar_chart(df["length"])

    elif run_button:
        st.warning("Please enter a company name or URL!")
    else:
        st.info("Enter a company name or URL and click 'Research Company' to start.")

if __name__=="__main__":
    main()
