import streamlit as st
import csv
import os
from datetime import date
import urllib.parse
import requests

# 1. Page Config (Must be the absolute first line)
st.set_page_config(page_title="AI Sales Command Center", layout="wide")

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
    # Fill defaults for rows
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
    # Selection of account
    selected_acc = st.selectbox("🎯 Target Account", [r[name_col].strip() for r in data])

    st.divider()

    # --- TOP ROW: DEEP INTELLIGENCE & RESEARCH ---
    col_research, col_outreach = st.columns(2)

    with col_research:
        st.subheader("🔍 Account Intelligence")
        
        # Quick Intelligence Buttons
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
                    query = f'"{selected_acc}" news expansion partnership 2025 2026'
                    res = requests.post(url, json={"q": query}, headers={'X-API-KEY': api_key})
                    search_hits = res.json().get("organic", [])
                    
                    if search_hits:
                        for item in search_hits[:3]:
                            st.info(f"**{item.get('title')}**\n\n{item.get('snippet')}")
                    else:
                        st.write("No specific recent news found. Try the LinkedIn button!")
                except Exception as e:
                    st.error(f"Agent Error: {e}")

    with col_outreach:
        st.subheader("📧 Outreach Generator")
        
        # Selection of the 'Hook'
        hook_type = st.radio("Choose your Hook Type:", ["Permit/Upgrade Hook", "Electricity Rate Video", "General Discovery"])
        
        if hook_type == "Permit/Upgrade Hook":
            subj = f"Question regarding refrigeration upgrades at {selected_acc}"
            body = f"Hi,\n\nI was looking into {selected_acc} and noticed some recent physical upgrades. Usually, when equipment changes at this scale, your utility rate class needs a manual review to avoid overpaying.\n\nI'd love to share how our database handles this for your specific zones.\n\nBest,\nLeke"
        elif hook_type == "Electricity Rate Video":
            subj = f"Rate Database Video for {selected_acc}"
            body = f"Hi,\n\nI thought you'd find this useful. Here is a quick video showing our current electricity rate database for {selected_acc} locations.\n\n[LINK TO VIDEO]\n\nBest,\nLeke"
        else:
            subj = f"Optimizing efficiency for {selected_acc}"
            body = f"Hi,\n\nI'd love to connect regarding how we are helping companies like {selected_acc} navigate shifting utility costs...\n\nBest,\nLeke"

        mailto_link = f"mailto:?subject={urllib.parse.quote(subj)}&body={urllib.parse.quote(body)}"
        btn_html = f'<a href="{mailto_link}" style="display:inline-block;width:100%;text-align:center;padding:12px;background:#ff4b4b;color:white;border-radius:8px;text-decoration:none;font-weight:bold;">📧 Create Email Draft</a>'
        st.markdown(btn_html, unsafe_allow_html=True)

    # --- MIDDLE ROW: PHYSICAL SIGNALS (PERMITS) ---
    st.divider()
    st.subheader("🏗️ Physical Signals & Permits")
    p_col1, p_col2 = st.columns(2)

    with p_col1:
        permit_query = f"{selected_acc} municipal permit refrigeration HVAC construction"
        permit_url = f"https://www.google.com/search?q={urllib.parse.quote(permit_query)}"
        st.link_button(f"🔎 Check Municipal Permits", permit_url, use_container_width=True)
        st.caption("Look for: HVAC, Refrigeration, or Solar permits.")

    with p_col2:
        bz_query = f"site:buildzoom.com {selected_acc}"
        bz_url = f"https://www.google.com/search?q={urllib.parse.quote(bz_query)}"
        st.link_button(f"🏗️ View BuildZoom History", bz_url, use_container_width=True)
        st.caption("Aggregated construction data and contractor history.")

    # --- BOTTOM ROW: TRACKER & DATABASE ---
    st.divider()
    st.subheader("📝 Activity Tracker")
    with st.form("update_activity"):
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            status = st.selectbox("New Status", ["Not Started", "Email Sent", "Call Made", "Conversation Had", "Meeting Booked"])
        with t_col2:
            notes = st.text_input("Log Notes")
        
        if st.form_submit_button("Update Activity Log"):
            for row in data:
                if row[name_col].strip() == selected_acc:
                    row['Last Outreach'] = str(date.today())
                    row['Status'] = status
                    row['Notes'] = notes
            
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=cols)
                writer.writeheader()
                writer.writerows(data)
            st.success(f"Log Updated for {selected_acc}!")
            st.rerun()

    st.subheader("📊 Full Prospect Database")
    st.dataframe(data, use_container_width=True)
