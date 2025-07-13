import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Load service account credentials from Streamlit secrets
    # Ensure your .streamlit/secrets.toml has 'gcp_service_account' configured
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"❌ Error loading Google service account credentials. Make sure 'gcp_service_account' is correctly configured in your Streamlit secrets. Details: {e}")
    st.stop() # Stop the app if credentials cannot be loaded

# --- Sheet Initialization ---
try:
    # IMPORTANT: This line opens your main Google Spreadsheet by its exact name
    spreadsheet = client.open("apexnuera_data") # Your Google Sheet name

    # IMPORTANT: These lines get specific tabs (worksheets) within that spreadsheet
    # Ensure these names match your Google Sheet tab names EXACTLY (case-sensitive)
    courses_sheet = spreadsheet.worksheet("Courses")
    jobs_sheet = spreadsheet.worksheet("Jobs")

except gspread.exceptions.SpreadsheetNotFound:
    st.error("❌ Google Spreadsheet named 'apexnuera_data' not found. Please ensure it exists and the service account has access.")
    st.stop()
except gspread.exceptions.WorksheetNotFound as e:
    st.error(f"❌ Error: One of the required worksheets was not found. Please ensure sheets named 'Courses' and 'Jobs' exist in your 'apexnuera_data' Google Sheet. Details: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ An unexpected error occurred during Google Sheets initialization: {e}")
    st.stop()


# --- Helper Functions ---

def get_data(sheet_name):
    """
    Fetches all records from a specified sheet.
    Args:
        sheet_name (str): The name of the sheet to fetch data from ("Courses" or "Jobs").
    Returns:
        list: A list of dictionaries, where each dictionary represents a row.
    """
    try:
        if sheet_name == "Courses":
            return courses_sheet.get_all_records()
        elif sheet_name == "Jobs":
            return jobs_sheet.get_all_records()
        return [] # Return empty list for invalid sheet_name
    except Exception as e:
        st.error(f"❌ Error fetching data from {sheet_name} sheet: {e}")
        return []

def delete_entry(sheet_name, column_name, selected_value):
    """
    Deletes an entry from a specified sheet based on column name and value.
    This function finds the first matching row and deletes it.
    Args:
        sheet_name (str): The name of the sheet to delete from ("Courses" or "Jobs").
        column_name (str): The header name of the column to match against (e.g., "Course Name").
        selected_value (str): The value to search for in the specified column.
    Returns:
        bool: True if an entry was successfully deleted, False otherwise.
    """
    target_sheet = None
    if sheet_name == "Courses":
        target_sheet = courses_sheet
    elif sheet_name == "Jobs":
        target_sheet = jobs_sheet
    else:
        st.error(f"❌ Invalid sheet name provided for deletion: {sheet_name}")
        return False

    data = get_data(sheet_name)
    if not data: # No data to process in the sheet
        st.info(f"No data found in '{sheet_name}' sheet to perform deletion.")
        return False

    row_to_delete_index = -1 # Initialize with an invalid index

    # Iterate through the fetched data (which is 0-indexed and excludes header)
    for idx, row in enumerate(data):
        # Ensure the column exists in the row dictionary and perform a robust comparison
        # .strip().lower() handles leading/trailing whitespace and case-insensitivity
        if column_name in row and str(row[column_name]).strip().lower() == str(selected_value).strip().lower():
            # gspread's delete_row expects a 1-based row number from the actual sheet.
            # Since get_all_records() skips the header row (row 1),
            # a 0-indexed 'idx' in the data list corresponds to 'idx + 2' in the sheet.
            row_to_delete_index = idx + 2
            break # Found the first match, stop searching

    if row_to_delete_index != -1:
        try:
            target_sheet.delete_row(row_to_delete_index)
            return True
        except Exception as e:
            st.error(f"❌ Error deleting row from '{sheet_name}' at actual sheet row {row_to_delete_index}: {e}")
            return False
    else:
        # This occurs if no matching value was found in the specified column
        return False

# ---------------- Streamlit App Layout ----------------

st.title("📊 Apexneura HR Panel")

---

## ➕ Add Course
course = st.text_input("Course Name", key="add_course_name_input")
timing = st.text_input("Course Timing", key="add_course_timing_input")

if st.button("Add Course", key="add_course_button"):
    if course and timing:
        try:
            courses_sheet.append_row([course, timing]) # Appends to the 'Courses' sheet
            st.success("✅ Course added successfully!")
            st.experimental_rerun() # Rerun to refresh the delete selection box
        except Exception as e:
            st.error(f"❌ Error adding course: {e}")
    else:
        st.warning("⚠️ Please fill both 'Course Name' and 'Course Timing' fields.")

---

## ➕ Add Job Opening
job = st.text_input("Job Opening", key="add_job_opening_input")

if st.button("Add Job", key="add_job_button"):
    if job:
        try:
            jobs_sheet.append_row([job]) # Appends to the 'Jobs' sheet
            st.success("✅ Job opening added successfully!")
            st.experimental_rerun() # Rerun to refresh the delete selection box
        except Exception as e:
            st.error(f"❌ Error adding job opening: {e}")
    else:
        st.warning("⚠️ Please enter a job opening.")

---

## 🗑️ Delete Course
st.subheader("🗑️ Delete Course")
# Fetch data specifically for the 'Courses' sheet for display in selectbox
course_data_for_delete = get_data("Courses")
# Filter out any rows that might not have a "Course Name" (though unlikely with proper adds)
courses_to_display = [row["Course Name"] for row in course_data_for_delete if row.get("Course Name")]

if courses_to_display:
    # Use unique keys for Streamlit widgets to avoid conflicts
    selected_course = st.selectbox("Select course to delete", courses_to_display, key="delete_course_select")
    if st.button("Delete Course", key="delete_course_button"):
        # Call delete_entry specifically for the 'Courses' sheet, matching by "Course Name"
        if delete_entry("Courses", "Course Name", selected_course):
            st.success(f"✅ Deleted course: **{selected_course}**")
            st.experimental_rerun() # Rerun to update the app state
        else:
            st.error("❌ Could not delete. Course not found or an unexpected error occurred during deletion.")
else:
    st.info("No courses available to delete.")

---

## 🗑️ Delete Job Opening
st.subheader("🗑️ Delete Job Opening")
# Fetch data specifically for the 'Jobs' sheet for display in selectbox
job_data_for_delete = get_data("Jobs")
# Filter out any rows that might not have a "Job Opening"
jobs_to_display = [row["Job Opening"] for row in job_data_for_delete if row.get("Job Opening")]

if jobs_to_display:
    selected_job = st.selectbox("Select job to delete", jobs_to_display, key="delete_job_select")
    if st.button("Delete Job", key="delete_job_button"):
        # Call delete_entry specifically for the 'Jobs' sheet, matching by "Job Opening"
        if delete_entry("Jobs", "Job Opening", selected_job):
            st.success(f"✅ Deleted job: **{selected_job}**")
            st.experimental_rerun()
        else:
            st.error("❌ Could not delete. Job not found or an unexpected error occurred during deletion.")
else:
    st.info("No job openings available to delete.")

---

## 🗑️ Delete Course Timing (Deletes associated course entry)
st.subheader("🗑️ Delete Course Timing (Deletes associated course entry)")
# Fetch data from the 'Courses' sheet as timings are part of course entries
course_data_for_timing_delete = get_data("Courses")
course_timings_to_display = [row["Course Timing"] for row in course_data_for_timing_delete if row.get("Course Timing")]

if course_timings_to_display:
    selected_timing = st.selectbox("Select timing to delete (deletes associated course entry)", course_timings_to_display, key="delete_timing_select")
    if st.button("Delete Timing", key="delete_timing_button"):
        # Call delete_entry for the 'Courses' sheet, but match by "Course Timing"
        if delete_entry("Courses", "Course Timing", selected_timing):
            st.success(f"✅ Deleted course entry with timing: **{selected_timing}**")
            st.experimental_rerun()
        else:
            st.error("❌ Could not delete. Timing not found or an unexpected error occurred during deletion.")
else:
    st.info("No course timings available to delete.")
