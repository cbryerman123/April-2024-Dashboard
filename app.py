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
        # We'll read the file as raw lists first to bypass the blank header issue
        reader = csv.reader(file)
        raw_rows = list(reader)
        
    if not raw_rows:
        st.error("The CSV file is empty!")
        st.stop()

    headers = raw_rows[0]
    data_rows = raw_rows[1:]

    # Ensure tracking columns exist in the header
    for col in ['Last Outreach', 'Status', 'Notes']:
        if col not in headers:
            headers.append(col)

    # Convert back to a list of dictionaries for Streamlit
    clean_data = []
    for row in data_rows:
        # Fill in shorter rows with empty strings
        while len(row) < len(headers):
            row.append("")
        
        # Create a dictionary mapping header to row value
        d = dict(zip(headers, row))
        
        # Default tracking values
        if not d.get('Status'): d['Status'] = 'Not Started'
        if not d.get('Last Outreach'): d['Last Outreach'] = 'None'
        
        clean_data.append(d)
            
    return clean_data, headers

data, headers = load_data()

st.title("🚀 Leke's March Focus: BDR Dashboard")

# We are going to find the FIRST column that actually has text in it
# This bypasses the "" names entirely
first_valid_col_index = 0
for i, h in enumerate(headers):
    # If the header is blank, we'll name it 'Account_Name' so we can use it
    if h == "":
        headers[i] = f"Column_{i+1}"

# Let's assume your names are in the very first column
name_column = headers[0]

st.subheader(f"Project List")
st.dataframe(data, use_container_width=True)

st.divider()
st.subheader("Update Activity")

# Get the names from that first column
account_names = [row[name_column] for row in data if row.get(name_column)]

with st.form("update_form"):
    selected_account = st.selectbox("Select Account", account_names)
    new_status = st.selectbox("Activity Status", ["Email Sent", "Call Made", "Conversation Had", "Meeting Booked"])
    new_notes = st.text_area("Notes")
    submit = st.form_submit_button("Save Update")

    if submit:
        for row in data:
            if row.get(name_column) == selected_account:
                row['Last Outreach'] = str(date.today())
                row['Status'] = new_status
                row['Notes'] = new_notes
        
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        
        st.success(f"Updated {selected_account}!")
        st.rerun()
