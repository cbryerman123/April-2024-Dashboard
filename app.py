import streamlit as st
import csv
import os
from datetime import date
import urllib.parse
import requests

# 1. Page Config - MUST be first
st.set_page_config(page_title="AI Sales Command Center", layout="wide")

# Ensure this matches your GitHub filename exactly
file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

# --- DATA LOADING ---
def load_data():
    if not os.path.exists(file_path):
        return [], []
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader if any(row.values())]
        cols = [c.strip() for c in reader.fieldnames] if reader.fieldnames else []
    for c in ['Last Outreach', 'Status', 'Notes']:
        if c not in cols: cols.append(c)
    for row in data:
        if not row.get('Status'): row['Status'] = 'Not Started'
        if not row.get('Last Outreach'): row['Last Outreach'] = 'None'
        if not row.get('Notes'): row['Notes'] = ''
    return data, cols

data, cols = load_data()

# --- APP START ---
st.title("🤖 AI Sales Command Center")

if not data:
    st.error(f"⚠️ Cannot find {file_path}. Check GitHub filename!")
else:
    name_col = cols[0]
    selected_acc = st.selectbox("🎯 Target Account", [r[name_col].strip() for r in data])

    st.divider()

    # --- TOP ROW: RESEARCH & OUTREACH ---
    col_res, col_out = st.columns(2)

    with col_res:
        st.subheader("🔍 Account Intelligence")
        c1, c2, c3 = st.columns(3)
        li_url = f"https://www.linkedin.com/search/results/content/?keywords={urllib.parse.quote(selected_acc)}"
        fin_url = f"https://www.google.com/finance/quote/{urllib.parse.quote(selected_acc)}"
        map_url = f"https://www.google.com/maps/search/{urllib.parse.quote(selected_acc)}"
        
        c1.link_button("📱 LI Posts", li_url, use_container_width=True)
        c2.link_button("📈 Market", fin_url, use_container_width=True)
        c3.link_button("📍 Maps", map_url, use_container_width=True)
        
        if st.button(f"Run News Agent", use_container_width=True):
            if "SERPER_API_KEY" not in st.secrets:
                st.warning("Add SERPER_API_KEY to Streamlit Secrets!")
            else:
                try:
                    url = "https://google.serper.dev/search"
                    headers = {'X-API-KEY': st.secrets["SERPER_API_KEY"]}
                    q = f'"{selected_acc}" news expansion energy'
                    res = requests.post(url, json={"q": q}, headers=headers)
                    hits = res.json().get("organic", [])
                    if hits:
                        for h in hits[:3]:
                            st.info(f"**{h.get('title')}**\n\n{h.get('snippet')}")
                    else:
                        st.write("No news found. Try LinkedIn!")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col_out:
        st.subheader("📧 Outreach Generator")
        hook = st.radio("Strategy:", ["Permit Hook", "Video", "General"])
        
        if hook == "Permit Hook":
            subj = f"Upgrades at {selected_acc}"
            body = f"Hi,\n\nI noticed recent upgrades at {selected_acc}. These changes often mean you qualify for a better utility rate. Let's chat.\n\nBest,\nLeke"
        elif hook == "Video":
            subj = f"Rate Video for {selected_acc}"
            body = f"Hi,\n\nHere is a video showing our electricity rate database for {selected_acc} locations.\n\n[LINK]\n\nBest,\nLeke"
        else:
            subj = f"Efficiency for {selected_acc}"
            body = f"Hi,\n\nI'd love to connect regarding energy costs at {selected_acc}...\n\nBest,\nLeke"

        mailto = f"mailto:?subject={urllib.parse.quote(subj)}&body={urllib.parse.quote(body)}"
        btn_code = f'<a href="{mailto}" style="display:inline-block;width:100%;text-align:center;padding:12px;background:#ff4b4b;color:white;border-radius:8px;text-decoration:none;font-weight:bold;">📧 Draft Email</a>'
        st.markdown(btn_code, unsafe_allow_html=True)

    # --- MIDDLE ROW: PHYSICAL SIGNALS ---
    st.divider()
    st.subheader("🏗️ Physical Signals (Permits)")
    p_col1, p_col2 = st.columns(2)

    with p_col1:
        if st.button(f"🔍 Fetch Permit Data", use_container_width=True):
            if "SERPER_API_KEY" in st.secrets:
                with st.spinner("Searching..."):
                    try:
                        q_p = f"{selected_acc} municipal permit refrigeration HVAC"
                        r_p = requests.post("https://google.serper.dev/search", json={"q": q_p}, headers={'X-API-KEY': st.secrets["SERPER_API_KEY"]})
                        res_p = r_p.json().get("organic", [])
                        if res_p:
                            for p in res_p[:3]:
                                st.write(f"📝 {p.get('snippet')}")
                                st.caption(f"[Source]({p.get('link')})")
                                st.divider()
                        else: st.info("No snippets found.")
                    except Exception as e: st.error(f"Error: {e}")
            else: st.warning("API Key missing!")
        
    with p_col2:
        bz_url = f"https://www.google.com/search?q=site:buildzoom.com {urllib.parse.quote(selected_acc)}"
        st.link_button("🏗️ BuildZoom History", bz_url, use_container_width=True)

    # --- BOTTOM ROW: TRACKER ---
    st.divider()
    st.subheader("📝 Activity Tracker")
    with st.form("log_entry"):
        t1, t2 = st.columns(2)
        st_val = t1.selectbox("Status", ["Not Started", "Email Sent", "Call Made", "Meeting Booked"])
        notes_val = t2.text_input("Notes")
        if st.form_submit_button("Save Log"):
            for row in data:
                if row[name_col].strip() == selected_acc:
                    row['Last Outreach'] = str(date.today())
                    row['Status'] = st_val
                    row['Notes'] = notes_val
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=cols)
                writer.writeheader()
                writer.writerows(data)
            st.success("Saved!")
            st.rerun()

    st.subheader("📊 Full Database")
    st.dataframe(data, use_container_width=True)
