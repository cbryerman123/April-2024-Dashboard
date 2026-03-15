import streamlit as st
import csv
import os
from datetime import date
import urllib.parse
import requests

# 1. Page Config must be the absolute first line
st.set_page_config(page_title="BDR Sales Command Center", layout="wide")

file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

# --- DATA PERSISTENCE ---
def load_data():
    if not os.path.exists(file_path):
        return [], []
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader if any(row.values())]
        cols = [c.strip() for c in reader.fieldnames] if reader.fieldnames else []
    for c in ['Last Outreach', 'Status', 'Notes']:
        if c not in cols: cols.append(c)
    return data, cols

data, cols = load_data()

# --- THE UI ---
st.title("🤖 AI Sales Command Center")

if not data:
    st.error(f"⚠️ Could not find your CSV file: {file_path}")
else:
    name_col = cols[0]
    
    # Selection Row
    selected_acc = st.selectbox("🎯 Target Account", [r[name_col] for r in data])

    # --- SECTION: AI AGENT ---
    st.divider()
    col_research, col_outreach = st.columns(2)

    with col_research:
        st.subheader("🔍 AI Research Agent")
        if st.button(f"Search news for {selected_acc}"):
            try:
                # Check for API Key
                if "SERPER_API_KEY" not in st.secrets:
                    st.warning("⚠️ API Key missing from Streamlit Secrets.")
                else:
                    api_key = st.secrets["SERPER_API_KEY"]
                    url = "https://google.serper.dev/news"
                    # We expanded the search terms to find MORE news
                    payload = {"q": f"{selected_acc} business news expansion"}
                    res = requests.post(url, json=payload, headers={'X-API-KEY': api_key})
                    news = res.json().get("news", [])
                    
                    if news:
                        for item in news[:3]:
                            st.write(f"✅ **{item['title']}**")
                            st.caption(f"Source: {item.get('source', 'Web')} | {item.get('date', 'Recent')}")
                    else:
                        st.info("No hyper-specific news found. Agent suggests checking LinkedIn.")
            except Exception as e:
                st.error(f"Agent Error: {e}")

    with col_outreach:
        st.subheader("📧 Outreach Generator")
        subj = f"Strategy for {selected_acc}"
        body = f"Hi,\n\nI was looking into {selected_acc} and wanted to share this video regarding your electricity rate database.\n\nBest,\nLeke"
        mailto = f"mailto:?subject={urllib.parse.quote(subj)}&body={urllib.parse.quote(body)}"
        st.markdown(f'<a href="{mailto}" style="display:inline-block;width:100%;text-align:center;padding:10px;background:#ff4b4
