import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Streamlit UI
st.title("Apexnuera HR Panel")

# --- Google Sheets Setup ---
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

    st.warning("Select the row(s) you wish to delete using the checkboxes below.")

    # Let's add a checkbox next to each row for deletion
    rows_to_delete = []
    st.write("---")
    st.subheader("Select Rows to Delete")

    # To ensure consistent layout for checkboxes and data
    # Create columns for the display and a separate one for the checkbox
    display_cols = st.columns(3) # For Course, Opening, Timing

    # Create a list to hold the state of each checkbox
    checkbox_states = [False] * len(df)

    for i, row in df.iterrows():
        # Display data in the first three columns
        with display_cols[0]:
            st.write(row.get("Course Name", "N/A")) # Use .get() for safety
        with display_cols[1]:
            st.write(row.get("Job Opening", "N/A"))
        with display_cols[2]:
            st.write(row.get("Course Timing", "N/A"))

        # Add checkbox in a separate column to the right
        if st.checkbox(f"Delete", key=f"delete_row_{i}"):
            rows_to_delete.append(i + 2) # +2 because sheets are 1-indexed and header row

    st.write("---") # Separator before the delete button

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
