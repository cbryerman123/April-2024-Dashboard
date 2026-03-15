import csv
import os
from datetime import date
import streamlit as st
import urllib.parse

st.set_page_config(page_title="BDR Sales Command Center", layout="wide")
file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

# --- HELPER FUNCTIONS ---
def load_data():
    if not os.path.exists(file_path):
        st.error(f"Could not find {file_path}")
        st.stop()
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader if any(row.values())]
        fieldnames = [f.strip() for f in reader.fieldnames] if reader.fieldnames else []
    for col in ['Last Outreach', 'Status', 'Notes']:
        if col not in fieldnames: fieldnames.append(col)
    return data, fieldnames

data, fieldnames = load_data()
name_col = fieldnames[0]

# --- DASHBOARD UI ---
st.title("🚀 BDR Sales Command Center")

# Search/Filter Bar
search_query = st.text_input("🔍 Quick Search Accounts", "")
filtered_data = [row for row in data if search_query.lower() in row[name_col].lower()]

st.subheader("Target List")
st.dataframe(filtered_data, use_container_width=True)

st.divider()

# --- THE MAGIC PART: EMAIL GENERATOR ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Log Activity")
    account_names = [row[name_col] for row in data if row.get(name_col) and row[name_col].strip()]
    
    with st.form("update_form"):
        selected_acc = st.selectbox("Select Account", account_names)
        new_status = st.selectbox("Status", ["Email Sent", "Call Made", "Meeting Booked", "Nurturing"])
        new_notes = st.text_area("Notes")
        if st.form_submit_button("Save Update"):
            for row in data:
                if row.get(name_col) == selected_acc:
                    row['Last Outreach'] = str(date.today()); row['Status'] = new_status; row['Notes'] = new_notes
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader(); writer.writerows(data)
            st.success("Saved!"); st.rerun()

with col2:
    st.subheader("2. Send Resources")
    resource = st.selectbox("Choose Resource to Send", ["Electricity Rate Database Video", "General Introduction", "Case Study"])
    
    # Define your templates here
    templates = {
        "Electricity Rate Database Video": {
            "subject": f"Quick question regarding electricity rates at {selected_acc}",
            "body": f"Hi,\n\nI thought you might find this useful. Here is a quick video of our signal showing the electricity rate database for {selected_acc}.\n\n[LINK TO VIDEO HERE]\n\nBest,\nLeke"
        },
        "General Introduction": {
            "subject": "Improving efficiency",
            "body": "Hi,\n\nI'd love to connect regarding your current processes..."
        }
    }

    selected_template = templates.get(resource, {"subject": "", "body": ""})
    
    # Show preview
    st.info(f"**Previewing Email for:** {selected_acc}")
    st.text_area("Subject Line", selected_template['subject'])
    st.text_area("Body Preview", selected_template['body'], height=150)

    # Create the Mailto Link
    subject_enc = urllib.parse.quote(selected_template['subject'])
    body_enc = urllib.parse.quote(selected_template['body'])
    mailto_link = f"mailto:?subject={subject_enc}&body={body_enc}"
    
    st.markdown(f'<a href="{mailto_link}" style="display: inline-block; padding
