# 1. Setup and Configuration
st.set_page_config(page_title="BDR Activity Dashboard", layout="wide")
file_path = "LEKE FOCUS FOR MARCH - Sheet1.csv"

# 2. Load the Data
def load_data():
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        
        # Automatically add tracking columns if they aren't in the CSV yet
        if 'Last Outreach' not in df.columns:
            df['Last Outreach'] = 'None'
        if 'Status' not in df.columns:
            df['Status'] = 'Not Started'
        if 'Notes' not in df.columns:
            df['Notes'] = ''
            
        return df
    else:
        st.error(f"Could not find {file_path}. Please make sure it's in the same folder.")
        st.stop()

df = load_data()

# 3. Dashboard Header & Metrics
st.title("🚀 Leke's March Focus: BDR Dashboard")

# Calculate metrics
total_accounts = len(df)
contacted_accounts = len(df[df['Status'] != 'Not Started'])

cols = st.columns(3)
cols[0].metric("Total Target Accounts", total_accounts)
cols[1].metric("Accounts Contacted", contacted_accounts)
cols[2].metric("Remaining to Contact", total_accounts - contacted_accounts)

# 4. The Interactive List
st.subheader("Current Priority List")
# Display the dataframe nicely
st.dataframe(df, use_container_width=True)

# 5. BDR Update Form (Data Entry)
st.divider()
st.subheader("Log New Activity")

with st.form("update_form"):
    # BDR selects the account they just worked on
    selected_account = st.selectbox("Select Account", df['Account'].dropna().unique())
    
    # BDR logs what happened
    new_status = st.selectbox("Activity Status", ["Email Sent", "Call Made", "Meeting Booked", "Follow Up Needed"])
    new_notes = st.text_area("Activity Notes (What happened?)")
    
    submit = st.form_submit_button("Update Record")

    if submit:
        # 6. Update the DataFrame
        # Find the row for the selected account and update the values
        df.loc[df['Account'] == selected_account, 'Last Outreach'] = str(date.today())
        df.loc[df['Account'] == selected_account, 'Status'] = new_status
        
        # Append new notes to existing notes if needed, or just overwrite
        df.loc[df['Account'] == selected_account, 'Notes'] = new_notes
        
        # Save back to the CSV file so it remembers the changes!
        df.to_csv(file_path, index=False)
        
        st.success(f"✅ Successfully logged activity for {selected_account}!")
        st.rerun() # Refreshes the app to show the new data