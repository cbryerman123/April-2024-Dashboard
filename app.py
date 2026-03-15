import csv
import os
from datetime import date
import streamlit as st
import urllib.parse
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="AI Sales Command Center", layout="wide")
file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

# --- AGENT FUNCTION: Research the Company ---
def research_company(company_name):
    try:
        # This is a 'Mini-Agent' that scrapes Google News for the company
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(company_name)}+news&tbm=nws"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        for item in soup.find_all('div', limit=3): # Get top 3 headlines
            title = item.find('div', attrs={'role': 'heading'})
            if title:
                articles.append(title.get_text())
        
        if not articles:
            return "No recent news found. Try a manual search."
        return "\n\n".join([f"• {a}" for a in articles])
    except:
        return "Research Agent is currently offline. Check connection."

# --- DATA LOADING ---
def load_data():
    if not os.path.exists(file_path):
        st.error(f"Could not find {file_path}"); st.stop()
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader if any(row.values())]
        fieldnames = [f.strip() for f in reader.fieldnames] if reader.fieldnames else []
    for col in ['Last Outreach', 'Status', 'Notes']:
        if col not in fieldnames: fieldnames.append(col)
    return data, fieldnames

data, fieldnames = load_data()
name_col = fieldnames[0]

# --- UI LAYOUT ---
st.title("🤖 AI Sales Command Center")

# 1. Selection Row
selected_acc = st.selectbox("Select Account to Target", [row[name_col] for row in data if row.get(name_col)])

# 2. The AI Agent Section
st.divider()
col_research, col_email = st.columns([1, 1])

with col_research:
    st.subheader(f"🔍 AI Research: {selected_acc}")
    if st.button(f"Run Agent Research for {selected_acc}"):
        with st.spinner("Agent is searching the web..."):
            results = research_company(selected_acc)
            st.markdown(f"**Latest News & Hooks:**\n\n{results}")
            st.caption("Use these as 'Hooks' in your outreach today.")
    else:
        st.info("Click the button above to have the AI Agent find today's talking points.")

with col_email:
    st.subheader("📧 Intelligence-Led Outreach")
    resource = st.selectbox("Topic", ["Electricity Rate Database", "Cost Reduction", "General Follow-up"])
    
    # Simple Logic: Personalize based on selection
    subject = f"Question for {selected_acc} team"
    body = f"Hi,\n\nI was just looking into {selected_acc} and noticed some interesting trends in the energy market. I thought you'd appreciate this video on the Electricity Rate Database...\n\nBest,\nLeke"
    
    st.text_area("Draft Preview", body, height=150)
    mailto = f"mailto:?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    st.markdown(f'<a href="{mailto}" style="display:inline-block;padding:10px;background-color:#ff4b4b;color:white;border-radius:5px;text-decoration:none;">Generate Email Draft</a>', unsafe_allow_html=True)

# 3. Data Table at the bottom
st.divider()
st.subheader("Full Tracking Database")
st.dataframe(data, use_container_width=True)
