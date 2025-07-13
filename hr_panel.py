import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Streamlit UI
st.title("Apexnuera HR Panel")

# --- Google Sheets Setup (same as before) ---
try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("apexnuera_data").sheet1
except Exception as e:
    st.error(f"❌ Error connecting to Google Sheets: {e}")
    st.stop() # Stop execution if connection fails

# --- Add New Data Section ---
st.header("➕ Add New Entry")
with st.form("add_data_form"):
    course = st.text_input("Enter Course Name", key="add_course")
    opening = st.text_input("Enter Job Opening", key="add_opening")
    timing = st.text_input("Enter Course Timing", key="add_timing")
    submit_button = st.form_submit_button("Submit New Entry")

    if submit_button:
        if course and opening and timing:
            try:
                sheet.append_row([course, opening, timing])
                st.success("✅ Data submitted successfully!")
                st.rerun() # Rerun to refresh the displayed data
            except Exception as e:
                st.error(f"❌ Error submitting data: {e}")
        else:
            st.warning("Please fill in all fields to add a new entry.")

---
## ➖ Delete Existing Entries

To enable deletion, we first need to display the current data from your Google Sheet. This allows users to see what's available and choose which row to remove. We'll use a **dataframe** for better visualization and selection.

```python
# --- Display and Delete Data Section ---
st.header("➖ Delete Existing Entries")

@st.cache_data(ttl=60) # Cache data for 60 seconds to reduce API calls
def load_data():
    """Loads data from Google Sheet into a Pandas DataFrame."""
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

df = load_data()

if not df.empty:
    st.dataframe(df, use_container_width=True)

    st.warning("Select the row(s) you wish to delete from the table above.")

    # Allow user to select row(s) for deletion
    # Streamlit's data editor can be used for selection
    edited_df = st.data_editor(df, num_rows="dynamic", hide_index=True)

    # Find the difference to identify deleted rows
    # This approach is suitable if you want to allow direct deletion via the editor
    # However, for explicit delete buttons, we'll use a different method below.

    # For explicit deletion, it's often clearer to have a separate "delete" column or selection
    # Let's add a checkbox next to each row for deletion
    rows_to_delete = []
    st.write("---")
    st.subheader("Select Rows to Delete (using checkboxes)")
    for i, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
        with col1:
            st.write(row["Course Name"]) # Assuming column names from your sheet
        with col2:
            st.write(row["Job Opening"])
        with col3:
            st.write(row["Course Timing"])
        with col4:
            if st.checkbox(f"Delete", key=f"delete_row_{i}"):
                rows_to_delete.append(i + 2) # +2 because sheets are 1-indexed and header row

    if st.button("Confirm Deletion", type="secondary"):
        if rows_to_delete:
            try:
                # Sort in reverse order to avoid issues with shifting row indices
                rows_to_delete.sort(reverse=True)
                for row_index in rows_to_delete:
                    sheet.delete_rows(row_index)
                st.success(f"🗑️ Successfully deleted {len(rows_to_delete)} row(s).")
                st.cache_data.clear() # Clear cache to force data reload
                st.rerun() # Rerun to refresh the displayed data
            except Exception as e:
                st.error(f"❌ Error deleting data: {e}")
        else:
            st.info("No rows selected for deletion.")
else:
    st.info("No data available in the sheet.")
