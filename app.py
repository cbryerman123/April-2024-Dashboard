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
        
    # Using utf-8-sig handles hidden characters at the start of Excel-saved CSVs
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        data = list(reader)
        # Clean column names (strip whitespace)
        fieldnames = [f.strip() for f in reader.fieldnames] if reader.fieldnames else []
        
    # Ensure our tracking columns exist in the list of headers
    for col in ['Last Outreach', 'Status', 'Notes']:
        if col not in fieldnames:
            fieldnames.append(col)
    
    # Clean up the data rows to match cleaned headers
    clean_data = []
    for row in data:
        clean_row = {k.strip(): v for k, v in row.items() if k}
        if 'Last Outreach' not in clean_row: clean_row['Last Outreach'] = 'None'
        if 'Status' not in clean_row: clean_row['Status'] = 'Not Started'
        if 'Notes' not in clean_row: clean_row['Notes'] = ''
        clean_data.append(clean_row)
        
    return clean_data, fieldnames

data, fieldnames = load_data()

st.title("🚀 Leke's March Focus: BDR Dashboard")

# Metric Calculations
total_accounts = len(data)
contacted_accounts = sum(1 for row in data if row.get('Status') != 'Not Started')

cols = st.columns(3)
cols[0].metric("Total Target Accounts", total_accounts)
cols[1].metric("Accounts Contacted", contacted_accounts)
cols[2].metric("Remaining", total_accounts - contacted_accounts)

# Display the Full Table
st.subheader("Full Prospect List")
st.dataframe(data, use_container_width=True)

st.divider()
st.subheader("Update Activity")

# Logic to find the 'Account' column even if it's named slightly differently
account_col = next((f for f in fieldnames if f.lower() == 'account'), None)

if account_col:
    # Create the list of names for the dropdown
    account_names = [row[account_col] for row in data if row.get(account_col)]
    
    with st.form("update_form"):
        selected_account = st.selectbox("Select Account", account_names)
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
else:
    st.error("Could not find a column named 'Account' in your file. Please check your CSV headers!")
