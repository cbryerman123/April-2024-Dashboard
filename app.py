import streamlit as st
import csv
import os
from datetime import date
import urllib.parse
import requests

# 1. Page Config (MUST be the absolute first line)
st.set_page_config(page_title="AI Sales Command Center", layout="wide")

file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

# --- DATA LOADING & PERSISTENCE ---
def load_data():
    if not os.path.exists(file_path):
        return [], []
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader if any(row.values())]
        cols = [c.strip() for c in reader.fieldnames] if reader.fieldnames else []
    
    # Ensure tracking columns exist in the system
    for c in ['Last Outreach', 'Status', 'Notes']:
        if c not in cols:
            cols.append(c)
            
    # Fill defaults for existing rows
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
    # We use the first column (usually 'Account') as the primary key
    name_col = cols[0]
    selected_acc = st.selectbox("🎯 Select Target Account", [r[name_col].strip() for r in data])

    st.divider()

    # --- TOP ROW: DEEP INTELLIGENCE & RESEARCH ---
    col_research, col_outreach = st.columns(2)

    with col_research:
        st.subheader("🔍 Account Intelligence")
        
        # Quick-Link Action Row
        c1, c2, c3 = st.columns(3)
        li_posts_url = f"https://www.linkedin.com/search/results/content/?keywords={urllib.parse.quote(selected_acc)}"
        finance_url = f"https://www.google.com/finance/quote/{urllib.parse.quote(selected_acc)}"
        maps_url = f"https://www.google.com/maps/search/{urllib.parse.quote(selected_acc)}"
        
        c1.link_button("📱 LI Activity", li_posts_url, use_container_width=True)
        c2.link_button("📈 Financials", finance_url, use_container_width=True)
        c3.link_button("📍 Map Locations", maps_url, use_container_width=True)
        
        st.write("")
        
        # AI News Agent
        if st.button(f"Run AI News Agent for {selected_acc}", use_container_width=True):
            if "SERPER_API_KEY" not in st.secrets:
                st.warning("API Key missing from Streamlit Secrets.")
            else:
                try:
                    api_key = st.secrets["SERPER_API_KEY"]
                    url = "https://google.serper.dev/search"
                    query = f'"{selected_acc}" news expansion partnership energy 2026'
                    res = requests.post(url, json={"q": query}, headers={'X-API-KEY': api_key})
                    search_hits = res.json().get("organic", [])
                    
                    if search_hits:
                        for item in search_hits[:3]:
                            st.info(f"**{item.get('title')}**\n\n{item.get('snippet')}")
                    else:
                        st.write("No specific recent news found. Use the LinkedIn button above!")
                except Exception as e:
                    st.error(f"Agent Error: {e}")

    with col_outreach:
        st.subheader("📧 Intelligence-Led Outreach")
        
        # Dynamic Hook Selection
        hook_type = st.radio("Choose Outreach Strategy:", ["Permit/Upgrade Hook", "Electricity Rate Video", "General Discovery"])
        
        if hook_type == "Permit/Upgrade Hook":
            subj = f"Question regarding recent upgrades at {selected_acc}"
            body = f"Hi,\n\nI was looking into {selected_acc} and noticed some recent mechanical/facility upgrades. Usually, when equipment changes at this scale, your utility rate class needs a manual review to avoid overpaying. I'd love to share how our database handles this for your zones.\n\nBest,\nLeke"
        elif hook_type == "Electricity Rate Video":
            subj = f"Rate Database Video for {selected_acc}"
            body = f"Hi,\n\nI thought you'd find this useful. Here is a quick video showing our current electricity rate database for {selected_acc} locations.\n\n[LINK TO VIDEO]\n\nBest,\nLeke"
        else:
            subj = f"Utility cost optimization for {selected_acc}"
            body =
