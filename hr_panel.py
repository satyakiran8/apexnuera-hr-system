import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

# Open specific sheets
try:
    # Ensure you have sheets named "Courses" and "Jobs" in your Google Sheet
    courses_sheet = client.open("apexneura_data").worksheet("Courses")
    jobs_sheet = client.open("apexneura_data").worksheet("Jobs")
except gspread.exceptions.WorksheetNotFound as e:
    st.error(f"Error: One of the required worksheets was not found. Please ensure 'Courses' and 'Jobs' sheets exist in your 'apexneura_data' Google Sheet. Details: {e}")
    st.stop() # Stop the app if sheets are not found

# --- Helper Functions ---

def get_data(sheet_name):
    """Fetches all records from a specified sheet."""
    if sheet_name == "Courses":
        return courses_sheet.get_all_records()
    elif sheet_name == "Jobs":
        return jobs_sheet.get_all_records()
    return []

def delete_entry(sheet_name, column_name, selected_value):
    """Deletes an entry from a specified sheet based on column name and value."""
    target_sheet = None
    if sheet_name == "Courses":
        target_sheet = courses_sheet
    elif sheet_name == "Jobs":
        target_sheet = jobs_sheet
    else:
        return False # Invalid sheet name

    data = get_data(sheet_name)
    for idx, row in enumerate(data):
        # Ensure the column exists in the row dictionary and compare values
        if column_name in row and str(row[column_name]).strip().lower() == str(selected_value).strip().lower():
            # gspread row numbers are 1-based.
            # get_all_records() gives 0-indexed list of rows, excluding header.
            # So, to delete the correct row, we add 1 for the 1-based index and
            # another 1 for the header row, resulting in idx + 2.
            target_sheet.delete_row(idx + 2)
            return True
    return False

# ---------------- Streamlit App Layout ----------------

st.title("📊 Apexneura HR Panel")

---

## ➕ Add Course
course = st.text_input("Course Name")
timing = st.text_input("Course Timing")

if st.button("Add Course"):
    if course and timing:
        courses_sheet.append_row([course, timing]) # Append only to courses sheet
        st.success("✅ Course added.")
        st.experimental_rerun() # Rerun to refresh deletion options
    else:
        st.warning("⚠️ Please fill both fields.")

---

## ➕ Add Job Opening
job = st.text_input("Job Opening")

if st.button("Add Job"):
    if job:
        jobs_sheet.append_row([job]) # Append only to jobs sheet
        st.success("✅ Job opening added.")
        st.experimental_rerun() # Rerun to refresh deletion options
    else:
        st.warning("⚠️ Enter a job opening.")

---

## 🗑️ Delete Course
# Fetch data specifically for courses
course_data = get_data("Courses")
# Filter out empty entries for the selectbox
courses = [row["Course Name"] for row in course_data if row.get("Course Name")]

if courses:
    # Use a unique key for selectbox to avoid conflicts
    selected_course = st.selectbox("Select course to delete", courses, key="delete_course_select")
    if st.button("Delete Course", key="delete_course_button"):
        if delete_entry("Courses", "Course Name", selected_course):
            st.success(f"✅ Deleted course: {selected_course}")
            st.experimental_rerun() # Rerun to reflect changes
        else:
            st.error("❌ Could not delete. Course not found.")
else:
    st.info("No courses to delete.")

---

## 🗑️ Delete Job Opening
# Fetch data specifically for jobs
job_data = get_data("Jobs")
# Filter out empty entries for the selectbox
jobs = [row["Job Opening"] for row in job_data if row.get("Job Opening")]

if jobs:
    # Use a unique key for selectbox to avoid conflicts
    selected_job = st.selectbox("Select job to delete", jobs, key="delete_job_select")
    if st.button("Delete Job", key="delete_job_button"):
        if delete_entry("Jobs", "Job Opening", selected_job):
            st.success(f"✅ Deleted job: {selected_job}")
            st.experimental_rerun() # Rerun to reflect changes
        else:
            st.error("❌ Could not delete. Job not found.")
else:
    st.info("No job openings to delete.")

---

## 🗑️ Delete Course Timing (Deletes entire course entry)
# Fetch data specifically for courses (timings are part of course entries)
course_data_for_timing = get_data("Courses")
# Filter out empty entries for the selectbox
course_timings = [row["Course Timing"] for row in course_data_for_timing if row.get("Course Timing")]

if course_timings:
    # Use a unique key for selectbox to avoid conflicts
    selected_timing = st.selectbox("Select timing to delete (deletes associated course entry)", course_timings, key="delete_timing_select")
    if st.button("Delete Timing", key="delete_timing_button"):
        # We are deleting from the 'Courses' sheet, matching by 'Course Timing'
        if delete_entry("Courses", "Course Timing", selected_timing):
            st.success(f"✅ Deleted course entry with timing: {selected_timing}")
            st.experimental_rerun() # Rerun to reflect changes
        else:
            st.error("❌ Could not delete. Timing not found.")
else:
    st.info("No course timings to delete.")
