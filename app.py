import streamlit as st
import csv
import os
from datetime import date
import urllib.parse
import requests

# 1. Page Config must be the absolute first line
st.set_page_config(page_title="BDR Sales Command Center", layout="wide")

file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

# --- DATA LOADING ---
def load_data():
    if not os.path.exists(file_path):
        return [], []
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader if any(row.values())]
        cols = [c.strip() for c in reader.fieldnames] if reader.fieldnames else []
    # Ensure tracking columns exist
    for c in ['Last Outreach', 'Status', 'Notes']:
        if c not in cols: cols.append(c)
    # Fill defaults
    for row in data:
        if not row.get('Status'): row['Status'] = 'Not Started'
        if not row.get('Last Outreach'): row['Last Outreach'] = 'None'
        if not row.get('Notes'): row['Notes'] = ''
    return data, cols

data, cols = load_data()

# --- APP START ---
st.title("🤖 AI Sales Command Center")

if not data:
    st.error(f"⚠️ CSV file not found or empty: {file_path}")
else:
    name_col = cols[0]
    selected_acc = st.selectbox("🎯 Target Account", [r[name_col] for r in data])

    st.divider()
    col_research, col_outreach = st.columns(2)

    with col_research:
        st.subheader("🔍 AI Research Agent")
        if st.button(f"Search news for {selected_acc}"):
            if "SERPER_API_KEY" not in st.secrets:
                st.warning("API Key missing from Secrets.")
            else:
                try:
                    api_key = st.secrets["SERPER_API_KEY"]
                    url = "https://google.serper.dev/news"
                    res = requests.post(url, json={"q": f"{selected_acc} news"}, headers={'X-API-KEY': api_key})
                    news = res.json().get("news", [])
                    if news:
                        for item in news[:3]:
                            st.write(f"✅ **{item['title']}**")
                            st.caption(f"{item.get('source', 'Web')} | {item.get('date', 'Recent')}")
                    else:
                        st.info("No specific news found. Check LinkedIn for updates.")
                except Exception as e:
                    st.error(f"Agent Error: {e}")

    with col_outreach:
        st.subheader("📧 Outreach Generator")
        subj = f"Strategy for {selected_acc}"
        body = f"Hi,\n\nI was looking into {selected_acc} and wanted to share this video regarding your electricity rate database.\n\nBest,\nLeke"
        mailto = f"mailto:?subject={urllib.parse.quote(subj)}&body={urllib.parse.quote(body)}"
        # Fixed the missing quote here that caused the SyntaxError
        btn_html = f'<a href="{mailto}" style="display:inline-block;width:100%;text-align:center;padding:10px;background:#ff4b4b;color:white;border-radius:5px;text-decoration:none;">📧 Create Email Draft</a>'
        st.markdown(btn_html, unsafe_allow_html=True)

    st.divider()
    st.subheader("📝 Activity Tracker")
    with st.form("update_activity"):
        c1, c2 = st.columns(2)
        with c1:
            status = st.selectbox("New Status", ["Not Started", "Email Sent", "Call Made", "Meeting Booked"])
        with c2:
            notes = st.text_input("Notes")
        if st.form_submit_button("Update Record"):
            for row in data:
                if row[name_col] == selected_acc:
                    row['Last Outreach'] = str(date.today())
                    row['Status'] = status
                    row['Notes'] = notes
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=cols)
                writer.writeheader()
                writer.writerows(data)
            st.success("Activity Logged!")
            st.rerun()

    st.subheader("📊 Full Prospect Database")
    st.dataframe(data, use_container_width=True)
