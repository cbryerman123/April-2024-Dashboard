import streamlit as st
import csv
import os
from datetime import date
import urllib.parse
import requests

# Set page config FIRST - this prevents blank screens
st.set_page_config(page_title="BDR Command Center", layout="wide")

# --- FILE SETUP ---
file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

def load_data():
    if not os.path.exists(file_path):
        st.error(f"Cannot find {file_path}")
        return [], []
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader if any(row.values())]
        cols = [c.strip() for c in reader.fieldnames] if reader.fieldnames else []
    for c in ['Last Outreach', 'Status', 'Notes']:
        if c not in cols: cols.append(c)
    return data, cols

data, cols = load_data()

# --- APP START ---
if not data:
    st.warning("No data found. Check your CSV file.")
else:
    name_col = cols[0]
    st.title("🤖 AI Sales Command Center")
    
    # 1. Select Account
    selected_acc = st.selectbox("🎯 Target Account", [r[name_col] for r in data])
    
    # 2. Research Agent
    st.divider()
    if st.button(f"🔍 Research {selected_acc}"):
        try:
            api_key = st.secrets["SERPER_API_KEY"]
            url = "https://google.serper.dev/news"
            res = requests.post(url, json={"q": f"{selected_acc} news"}, headers={'X-API-KEY': api_key})
            news = res.json().get("news", [])
            if news:
                for item in news[:3]:
                    st.write(f"• **{item['title']}** ({item.get('date', 'Recent')})")
            else:
                st.write("No specific news found today.")
        except Exception as e:
            st.error("Agent is waiting for API Key. Check your 'Secrets' in Streamlit settings.")

    # 3. Email Generator
    st.divider()
    st.subheader("📧 Outreach")
    subj = f"Question for {selected_acc}"
    body = f"Hi,\n\nI was researching {selected_acc} and wanted to share this video...\n\nBest,\nLeke"
    mailto = f"mailto:?subject={urllib.parse.quote(subj)}&body={urllib.parse.quote(body)}"
    st.markdown(f'<a href="{mailto}" style="padding:10px;background:#ff4b4b;color:white;border-radius:5px;text-decoration:none;">Draft Email</a>', unsafe_allow_html=True)

    # 4. Data Table
    st.divider()
    st.subheader("📊 Tracker")
    st.dataframe(data, use_container_width=True)
