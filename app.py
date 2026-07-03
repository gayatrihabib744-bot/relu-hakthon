import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from google import genai
import time

st.set_page_config(page_title="Hackathon Dashboard", layout="wide")

API_KEY = "AQ.Ab8RN6IUk0ouq0A8TAmiM6w5D-m0S70nbvgutoCrRX90dpDuTA"
client = genai.Client(api_key=API_KEY)

def fetch_data(source_url):
    try:
        response = requests.get(source_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        for tag in soup.find_all("p")[:20]:
            text = tag.get_text(strip=True)
            if text:
                items.append({"content": text})
        if not items:
            st.warning("No data extracted.")
            return pd.DataFrame(columns=["content"])
        return pd.DataFrame(items)
    except Exception as e:
        st.error(f"Failed: {e}")
        return pd.DataFrame(columns=["content"])

def ai_process(text):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=f"Summarize in one sentence:\n\n{text[:2000]}"
        )
        return response.text
    except Exception as e:
        return f"AI temporarily unavailable. Data collected! Summary: {text[:2000]}..."

def main():
    st.title("🚀 Hackathon Pipeline Dashboard")
    st.caption("Data collection → AI processing → Visualization")
    with st.sidebar:
        st.header("Controls")
        source_url = st.text_input("Data source URL", value="https://quotes.toscrape.com")
        run_button = st.button("Run Pipeline", type="primary")
    if run_button:
        with st.spinner("Fetching data..."):
            df = fetch_data(source_url)
        if df.empty:
            st.stop()
        st.subheader("📥 Raw Data")
        st.dataframe(df, use_container_width=True)
        with st.spinner("Running AI..."):
            summary = ai_process(" ".join(df["content"].head(5).tolist()))
        st.subheader("🤖 AI Output")
        st.write(summary)
        st.subheader("📊 Stats")
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", len(df))
        col2.metric("Avg length", int(df["content"].str.len().mean()))
        col3.metric("Last run", time.strftime("%H:%M:%S"))
        df["length"] = df["content"].str.len()
        st.bar_chart(df["length"])
    else:
        st.info("Enter a source and click 'Run Pipeline' to start.")

if __name__ == "__main__":
    main()