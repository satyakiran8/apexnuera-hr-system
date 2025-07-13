import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set up the title
st.title("Apexnuera HR Panel")

# Set up credentials and access the Google Sheet
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(creds)
sheet = client.open("apexnuera_data").sheet1

# Fetch data from sheet
data = sheet.get_all_records()

# Helper functions
def update_sheet(new_row):
    sheet.append_row(new_row)

def delete_row_by_value(column_index, value):
    cell = sheet.find(value)
    if cell and cell.col == column_index:
        sheet.delete_rows(cell.row)

# Add Course Section
st.subheader("➕ Add Course")
course_name = st.text_input("Course Name")
course_time = st.text_input("Course Timing")
if st.button("Add Course"):
    if course_name and course_time:
        update_sheet([course_name, "", course_time])
        st.success("✅ Course added successfully")
    else:
        st.warning("⚠️ Please enter both course name and timing")

# Add Job Opening Section
st.subheader("➕ Add Job Opening")
job_opening = st.text_input("Job Opening")
if st.button("Add Job Opening"):
    if job_opening:
        update_sheet(["", job_opening, ""])
        st.success("✅ Job opening added successfully")
    else:
        st.warning("⚠️ Please enter job opening")

# Delete Course Section
st.subheader("🗑️ Delete Course")
courses = [row["Course Name"] for row in data if row["Course Name"]]
selected_course = st.selectbox("Select a course to delete", courses)
if st.button("Delete Course"):
    delete_row_by_value(1, selected_course)
    st.success(f"✅ Deleted course: {selected_course}")

# Delete Job Opening Section
st.subheader("🗑️ Delete Job Opening")
jobs = [row["Job Opening"] for row in data if row["Job Opening"]]
selected_job = st.selectbox("Select a job to delete", jobs)
if st.button("Delete Job Opening"):
    delete_row_by_value(2, selected_job)
    st.success(f"✅ Deleted job: {selected_job}")

# Delete Course Timing Section
st.subheader("🗑️ Delete Course Timing")
timings = [row["Course Timing"] for row in data if row["Course Timing"]]
selected_timing = st.selectbox("Select course timing to delete", timings)
if st.button("Delete Course Timing"):
    delete_row_by_value(3, selected_timing)
    st.success(f"✅ Deleted course timing: {selected_timing}")
