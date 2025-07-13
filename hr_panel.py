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

# --- Visual Separator for Streamlit UI ---
st.markdown("---")

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

    st.markdown("---") # Visual separator within the delete section
    st.subheader("Select Rows to Delete")

    # To ensure consistent layout for checkboxes and data when displaying for deletion
    # We'll manually create columns for each row
    rows_to_delete = []

    # Prepare data for display with checkboxes
    # Create a list of dictionaries where each dict represents a row with its data and a placeholder for checkbox
    display_data = []
    for i, row in df.iterrows():
        display_data.append({
            "Course Name": row.get("Course Name", "N/A"),
            "Job Opening": row.get("Job Opening", "N/A"),
            "Course Timing": row.get("Course Timing", "N/A"),
            "Select to Delete": False # Placeholder for checkbox in st.data_editor
        })

    # Convert to DataFrame for st.data_editor
    editable_df = pd.DataFrame(display_data)

    # Use st.data_editor for a more interactive and cleaner selection
    edited_df = st.data_editor(
        editable_df,
        column_config={
            "Select to Delete": st.column_config.CheckboxColumn(
                "Select to Delete",
                help="Select rows to delete",
                default=False,
            )
        },
        disabled=df.columns.tolist(), # Disable editing of data columns
        hide_index=True,
        use_container_width=True
    )

    # Identify rows marked for deletion
    # Checkbox state is in the 'Select to Delete' column of edited_df
    # We need to map this back to the original sheet index
    for i, row in edited_df.iterrows():
        if row["Select to Delete"]:
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
