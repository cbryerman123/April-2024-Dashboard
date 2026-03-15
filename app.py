import csv
import os
from datetime import date
import streamlit as st
import urllib.parse
import requests

# --- INITIAL SETUP ---
st.set_page_config(page_title="AI Sales Command Center", layout="wide")
file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

# --- AGENT FUNCTION: Research the Company via Serper.dev ---
def research_company(company_name):
    # This pulls the key from the 'Secrets' vault in Streamlit Settings
    try:
        api_key = st.secrets["SERPER_API_KEY"]
    except:
        return "❌ API Key not found in Streamlit Secrets. Please add SERPER_API_KEY."

    url = "https://google.serper.dev/news"
    payload = {"q": f"{company_name} news electricity sustainability"}
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        results = response.json()
        
        articles = []
        if "news" in results:
            for item in results["news"][:3]: # Grab top 3 results
                title = item.get('title', 'No Title')
                source = item.get('source', 'Unknown Source')
                date_str = item.get('date', 'Recently')
                articles.append(f"• **{title}**\n_{source} - {date_str}_")
        
        if not articles:
            return "No recent news found for this company. Try a manual search."
        return "\n\n".join(articles)
    except Exception as e:
        return f"Agent Error: {str(e)}"

# --- DATA LOADING & CLEANING ---
def load_data():
    if not os.path.exists(file_path):
        st.error(f"Could not find {file_path}. Please ensure your CSV is uploaded to GitHub.")
        st.stop()
        
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        # Filter out empty rows that plague CSVs
        data = [row for row in reader if any(row.values())]
        fieldnames = [f.strip() for f in reader.fieldnames] if reader.fieldnames else []
        
    # Ensure tracking columns exist in the header
    for col in ['Last Outreach', 'Status', 'Notes']:
        if col not in fieldnames:
            fieldnames.append(col)
    
    # Fill in default values for missing data
    for row in data:
        if not row.get('Status'): row['Status'] = 'Not Started'
        if not row.get('Last Outreach'): row
