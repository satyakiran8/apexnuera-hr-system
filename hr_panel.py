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

# --- Data Loading Utility ---
@st.cache_data(ttl=60) # Cache data for 60 seconds
def load_data():
    """Loads data from Google Sheet into a Pandas DataFrame."""
    try:
        data = sheet.get_all_records() # Gets list of dictionaries
        df = pd.DataFrame(data)
        # Ensure 'Course Name', 'Job Opening', 'Course Timing' columns exist
        for col in ["Course Name", "Job Opening", "Course Timing"]:
            if col not in df.columns:
                df[col] = "" # Add missing columns if any
        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame(columns=["Course Name", "Job Opening", "Course Timing"])

df = load_data()

# --- View All Data Section (for overview) ---
st.header("📊 Current Data Overview")
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data available in the sheet.")

st.markdown("---")

## 🎓 Course & Timing Management

st.header("🎓 Course & Timing Management")

# --- Add/Update Course & Timing ---
st.subheader("➕ Add New Course & Timing")
with st.form("add_course_timing_form"):
    add_course = st.text_input("Enter Course Name", key="add_course_ct")
    add_timing = st.text_input("Enter Course Timing", key="add_timing_ct")
    add_ct_button = st.form_submit_button("Add Course & Timing")

    if add_ct_button:
        if add_course and add_timing:
            try:
                # Find if course already exists to update, otherwise append new row
                # We'll just append for simplicity here, assuming new entries are new rows
                # For update, you'd need to find the row index.
                sheet.append_row([add_course, "", add_timing]) # Job Opening column will be empty
                st.success("✅ Course and Timing added successfully!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error adding Course & Timing: {e}")
        else:
            st.warning("Please fill in both Course Name and Course Timing.")

st.markdown("---")

# --- Delete Course & Timing (Row-based) ---
st.subheader("➖ Delete Course & Timing Entries")
if not df.empty:
    st.write("Select the Course & Timing row(s) to delete:")

    # Create a DataFrame for selection, focusing on Course Name and Course Timing
    ct_df = df[["Course Name", "Course Timing"]].copy()
    ct_df["Select to Delete"] = False # Add a column for checkboxes

    edited_ct_df = st.data_editor(
        ct_df,
        column_config={
            "Select to Delete": st.column_config.CheckboxColumn(
                "Select to Delete",
                help="Select rows to delete",
                default=False,
            )
        },
        disabled=ct_df.columns[:-1].tolist(), # Disable editing of data columns
        hide_index=True,
        use_container_width=True
    )

    rows_to_delete_ct = []
    for i, row in edited_ct_df.iterrows():
        if row["Select to Delete"]:
            rows_to_delete_ct.append(i + 2) # +2 for sheet indexing and header

    if st.button("Confirm Delete Selected Course & Timing", type="secondary", key="delete_ct_btn"):
        if rows_to_delete_ct:
            try:
                rows_to_delete_ct.sort(reverse=True) # Delete from bottom up
                for row_index in rows_to_delete_ct:
                    sheet.delete_rows(row_index)
                st.success(f"🗑️ Successfully deleted {len(rows_to_delete_ct)} Course & Timing row(s).")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error deleting Course & Timing: {e}")
        else:
            st.info("No Course & Timing rows selected for deletion.")
else:
    st.info("No Course & Timing data to delete.")

st.markdown("---")

## 💼 Job Opening Management

st.header("💼 Job Opening Management")

# --- Add/Update Specific Job Opening Cell ---
st.subheader("➕ Add/Update a Job Opening")
st.write("Enter the row number and the new Job Opening. Leave Job Opening blank to clear it.")

with st.form("add_update_job_form"):
    job_row_num = st.number_input("Enter Row Number (from 1-indexed sheet, e.g., 2 for first data row)", min_value=2, step=1, key="job_row_num")
    new_job_opening = st.text_input("New Job Opening (leave blank to clear cell)", key="new_job_opening")
    update_job_button = st.form_submit_button("Update Job Opening")

    if update_job_button:
        try:
            # Find the column index for "Job Opening"
            headers = sheet.row_values(1) # Get header row
            try:
                job_opening_col_index = headers.index("Job Opening") + 1 # +1 for 1-based indexing
            except ValueError:
                st.error("❌ 'Job Opening' column not found in your Google Sheet header!")
                st.stop()

            # Update the cell: sheet.update_cell(row, col, value)
            sheet.update_cell(job_row_num, job_opening_col_index, new_job_opening)
            st.success(f"✅ Job Opening in row {job_row_num} updated successfully!")
            st.cache_data.clear()
            st.rerun()
        except gspread.exceptions.APIError as api_e:
            st.error(f"❌ Google Sheets API Error: {api_e.response.text}")
        except Exception as e:
            st.error(f"❌ Error updating Job Opening: {e}")

st.markdown("---")

# --- Delete (Clear) Specific Job Opening Cells from a list ---
st.subheader("➖ Clear Specific Job Opening Entries")
st.write("Select the Job Opening cells you wish to clear.")

if not df.empty:
    # Display Job Opening column specifically
    job_openings_list = df["Job Opening"].tolist()
    
    selected_indices_to_clear = []

    for i, job_text in enumerate(job_openings_list):
        if job_text: # Only show checkbox if there's actual text
            if st.checkbox(f"Clear Job: {job_text} (Row {i+2})", key=f"clear_job_{i}"):
                selected_indices_to_clear.append(i + 2) # +2 for sheet indexing and header

    if st.button("Confirm Clear Selected Job Openings", type="secondary", key="clear_jobs_btn"):
        if selected_indices_to_clear:
            try:
                headers = sheet.row_values(1)
                job_opening_col_index = headers.index("Job Opening") + 1

                for row_index in selected_indices_to_clear:
                    sheet.update_cell(row_index, job_opening_col_index, "") # Set cell to empty
                st.success(f"🗑️ Successfully cleared {len(selected_indices_to_clear)} Job Opening cell(s).")
                st.cache_data.clear()
                st.rerun()
            except gspread.exceptions.APIError as api_e:
                st.error(f"❌ Google Sheets API Error: {api_e.response.text}")
            except Exception as e:
                st.error(f"❌ Error clearing Job Opening cells: {e}")
        else:
            st.info("No Job Opening cells selected to clear.")
else:
    st.info("No Job Opening data to clear.")
