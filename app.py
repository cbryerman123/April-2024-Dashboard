import csv
import os
from datetime import date
import streamlit as st

st.set_page_config(page_title="BDR Activity Dashboard", layout="wide")
file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

# Load the data using built-in Python tools (No Pandas needed!)
def load_data():
    if not os.path.exists(file_path):
        st.error(f"Could not find {file_path}")
        st.stop()
        
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        data = list(reader)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        
    # Add our tracking columns if they don't exist
    if 'Last Outreach' not in fieldnames: fieldnames.append('Last Outreach')
    if 'Status' not in fieldnames: fieldnames.append('Status')
    if 'Notes' not in fieldnames: fieldnames.append('Notes')
    
    for row in data:
        if 'Last Outreach' not in row: row['Last Outreach'] = 'None'
        if 'Status' not in row: row['Status'] = 'Not Started'
        if 'Notes' not in row: row['Notes'] = ''
        
    return data, fieldnames

data, fieldnames = load_data()

# Dashboard Header & Metrics
st.title("🚀 Leke's March Focus: BDR Dashboard")

total_accounts = len(data)
contacted_accounts = sum(1 for row in data if row.get('Status', 'Not Started') != 'Not Started')

cols = st.columns(3)
cols[0].metric("Total Target Accounts", total_accounts)
cols[1].metric("Accounts Contacted", contacted_accounts)
cols[2].metric("Remaining to Contact", total_accounts - contacted_accounts)

# The Interactive List
st.subheader("Current Priority List")
st.dataframe(data, use_container_width=True)

# BDR Update Form (Data Entry)
st.divider()
st.subheader("Log New Activity")

# Get unique accounts for the dropdown
accounts = list(set(row['Account'] for row in data if row.get('Account')))

with st.form("update_form"):
    selected_account = st.selectbox("Select Account", accounts)
    new_status = st.selectbox("Activity Status", ["Email Sent", "Call Made", "Meeting Booked", "Follow Up Needed"])
    new_notes = st.text_area("Activity Notes (What happened?)")
    submit = st.form_submit_button("Update Record")

    if submit:
        # Update the data
        for row in data:
            if row.get('Account') == selected_account:
                row['Last Outreach'] = str(date.today())
                row['Status'] = new_status
                row['Notes'] = new_notes
        
        # Save back to the CSV file
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        st.success(f"✅ Successfully logged activity for {selected_account}!")
        st.rerun()
