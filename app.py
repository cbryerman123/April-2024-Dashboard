import csv
import os
from datetime import date
import streamlit as st

st.set_page_config(page_title="BDR Activity Dashboard", layout="wide")
file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

def load_data():
    if not os.path.exists(file_path):
        st.error(f"Could not find {file_path}")
        st.stop()
        
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        data = list(reader)
        # We are going to get the REAL names of your columns here
        fieldnames = [f.strip() for f in reader.fieldnames] if reader.fieldnames else []
        
    for col in ['Last Outreach', 'Status', 'Notes']:
        if col not in fieldnames:
            fieldnames.append(col)
    
    clean_data = []
    for row in data:
        clean_row = {k.strip(): v for k, v in row.items() if k}
        for col in fieldnames:
            if col not in clean_row: clean_row[col] = ''
        if not clean_row.get('Status'): clean_row['Status'] = 'Not Started'
        clean_data.append(clean_row)
        
    return clean_data, fieldnames

data, fieldnames = load_data()

st.title("🚀 Leke's March Focus: BDR Dashboard")

# --- THIS PART IS THE FIX ---
# This shows us exactly what columns the computer sees
st.write("Debug: Your file columns are:", fieldnames)

st.subheader("Full Prospect List")
st.dataframe(data, use_container_width=True)

st.divider()
st.subheader("Update Activity")

# We will try to find the Account column. If it's not named 'Account', 
# we will just use the very first column in your file.
account_col = next((f for f in fieldnames if f.lower() == 'account'), fieldnames[0])

account_names = [row[account_col] for row in data if row.get(account_col)]

with st.form("update_form"):
    selected_account = st.selectbox(f"Select from {account_col}", account_names)
    new_status = st.selectbox("Activity Status", ["Email Sent", "Call Made", "Conversation Had", "Meeting Booked"])
    new_notes = st.text_area("Notes")
    submit = st.form_submit_button("Save Update")

    if submit:
        for row in data:
            if row.get(account_col) == selected_account:
                row['Last Outreach'] = str(date.today())
                row['Status'] = new_status
                row['Notes'] = new_notes
        
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        st.success(f"Updated {selected_account}!")
        st.rerun()
