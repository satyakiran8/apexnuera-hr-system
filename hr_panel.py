import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Load service account credentials from Streamlit secrets
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"❌ Error loading Google service account credentials. Make sure 'gcp_service_account' is correctly configured in your Streamlit secrets. Details: {e}")
    st.stop() # Stop the app if credentials cannot be loaded

# --- Sheet Initialization ---
try:
    # IMPORTANT CHANGE: Opening the spreadsheet named "apexnuera"
    spreadsheet = client.open("apexnuera") # Changed from "apexneura_data"

    # IMPORTANT: Verify these sheet names match EXACTLY what's in your Google Spreadsheet tabs
    courses_sheet = spreadsheet.worksheet("Courses")
    jobs_sheet = spreadsheet.worksheet("Jobs")

except gspread.exceptions.SpreadsheetNotFound:
    st.error("❌ Google Spreadsheet named 'apexnuera' not found. Please ensure it exists and the service account has access.")
    st.stop()
except gspread.exceptions.WorksheetNotFound as e:
    st.error(f"❌ Error: One of the required worksheets was not found. Please ensure sheets named 'Courses' and 'Jobs' exist in your 'apexnuera' Google Sheet. Details: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ An unexpected error occurred during Google Sheets initialization: {e}")
    st.stop()


# --- Helper Functions ---

def get_data(sheet_name):
    """Fetches all records from a specified sheet."""
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
    """Deletes an entry from a specified sheet based on column name and value."""
    target_sheet = None
    if sheet_name == "Courses":
        target_sheet = courses_sheet
    elif sheet_name == "Jobs":
        target_sheet = jobs_sheet
    else:
        st.error(f"❌ Invalid sheet name provided for deletion: {sheet_name}")
        return False

    data = get_data(sheet_name)
    if not data: # No data to process
        return False

    row_to_delete_index = -1 # Initialize with an invalid index

    for idx, row in enumerate(data):
        # IMPORTANT: Ensure the column name exists in the dictionary key
        # and perform case-insensitive, whitespace-stripped comparison.
        if column_name in row and str(row[column_name]).strip().lower() == str(selected_value).strip().lower():
            row_to_delete_index = idx + 2 # +2 for header row and 0-based index
            break # Found the first match, break the loop

    if row_to_delete_index != -1:
        try:
            target_sheet.delete_row(row_to_delete_index)
            return True
        except Exception as e:
            st.error(f"❌ Error deleting row from {sheet_name} at row {row_to_delete_index}: {e}")
            return False
    return False

# ---------------- Streamlit App Layout ----------------

st.title("📊 Apexneura HR Panel")

st.markdown("---")

## ➕ Add Course
course = st.text_input("Course Name", key="add_course_name")
timing = st.text_input("Course Timing", key="add_course_timing")

if st.button("Add Course", key="add_course_button"):
    if course and timing:
        try:
            courses_sheet.append_row([course, timing]) # Append only to courses sheet
            st.success("✅ Course added successfully!")
            st.experimental_rerun() # Rerun to refresh deletion options
        except Exception as e:
            st.error(f"❌ Error adding course: {e}")
    else:
        st.warning("⚠️ Please fill both Course Name and Course Timing fields.")

st.markdown("---")

## ➕ Add Job Opening
job = st.text_input("Job Opening", key="add_job_opening")

if st.button("Add Job", key="add_job_button"):
    if job:
        try:
            jobs_sheet.append_row([job]) # Append only to jobs sheet
            st.success("✅ Job opening added successfully!")
            st.experimental_rerun() # Rerun to refresh deletion options
        except Exception as e:
            st.error(f"❌ Error adding job opening: {e}")
    else:
        st.warning("⚠️ Please enter a job opening.")

st.markdown("---")

## 🗑️ Delete Course
st.subheader("🗑️ Delete Course")
# Fetch data specifically for courses
course_data_for_delete = get_data("Courses")
courses_to_display = [row["Course Name"] for row in course_data_for_delete if row.get("Course Name")]

if courses_to_display:
    selected_course = st.selectbox("Select course to delete", courses_to_display, key="delete_course_select")
    if st.button("Delete Course", key="delete_course_button"):
        if delete_entry("Courses", "Course Name", selected_course):
            st.success(f"✅ Deleted course: **{selected_course}**")
            st.experimental_rerun() # Rerun to reflect changes
        else:
            st.error("❌ Could not delete. Course not found or an error occurred.")
else:
    st.info("No courses available to delete.")

st.markdown("---")

## 🗑️ Delete Job Opening
st.subheader("🗑️ Delete Job Opening")
# Fetch data specifically for jobs
job_data_for_delete = get_data("Jobs")
jobs_to_display = [row["Job Opening"] for row in job_data_for_delete if row.get("Job Opening")]

if jobs_to_display:
    selected_job = st.selectbox("Select job to delete", jobs_to_display, key="delete_job_select")
    if st.button("Delete Job", key="delete_job_button"):
        if delete_entry("Jobs", "Job Opening", selected_job):
            st.success(f"✅ Deleted job: **{selected_job}**")
            st.experimental_rerun() # Rerun to reflect changes
        else:
            st.error("❌ Could not delete. Job not found or an error occurred.")
else:
    st.info("No job openings available to delete.")

st.markdown("---")

## 🗑️ Delete Course Timing (Deletes associated course entry)
st.subheader("🗑️ Delete Course Timing (Deletes associated course entry)")
course_data_for_timing_delete = get_data("Courses")
course_timings_to_display = [row["Course Timing"] for row in course_data_for_timing_delete if row.get("Course Timing")]

if course_timings_to_display:
    selected_timing = st.selectbox("Select timing to delete (deletes associated course)", course_timings_to_display, key="delete_timing_select")
    if st.button("Delete Timing", key="delete_timing_button"):
        if delete_entry("Courses", "Course Timing", selected_timing):
            st.success(f"✅ Deleted course entry with timing: **{selected_timing}**")
            st.experimental_rerun() # Rerun to reflect changes
        else:
            st.error("❌ Could not delete. Timing not found or an error occurred.")
else:
    st.info("No course timings available to delete.")
