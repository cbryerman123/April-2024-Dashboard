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
        fieldnames = [f.strip() for f in reader.fieldnames] if reader.fieldnames else []
        
    # Ensure tracking columns exist
    for col in ['Last Outreach', 'Status', 'Notes']:
        if col not in fieldnames:
            fieldnames.append(col)
    
    return data, fieldnames

data, fieldnames = load_data()

st.title("🚀 Leke's March Focus: BDR Dashboard")

# DETECTIVE WORK: Find the first column that isn't empty
# We'll skip the columns that are just "" and find the one with the names
real_data_col = None
for col in fieldnames:
    if col != "" and col not in ['Last Outreach', 'Status', 'Notes']:
        real_data_col = col
        break

# If we still can't find it, we'll just use the very first column
if not real_data_col:
    real_data_col = fieldnames[0]

# Display Table
st.subheader(f"Project List (Tracking by: {real_data_col})")
st.dataframe(data, use_container_width=True)

st.divider()
st.subheader("Update Activity")

# Dropdown Menu
account_names = [row[real_data_col] for row in data if row.get(real_data_col)]

with st.form("update_form"):
    selected_account = st.selectbox(f"Select {real_data_col}", account_names)
    new_status = st.selectbox("Activity Status", ["Email Sent", "Call Made", "Conversation Had", "Meeting Booked"])
    new_notes = st.text_area("Notes")
    submit = st.form_submit_button("Save Update")

    if submit:
        for row in data:
            if row.get(real_data_col) == selected_account:
                row['Last Outreach'] = str(date.today())
                row['Status'] = new_status
                row['Notes'] = new_notes
        
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        st.success(f"Updated {selected_account}!")
        st.rerun()
