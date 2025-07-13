import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Setup Google Sheets connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)
sheet = client.open("apexneura_data").sheet1

# Helper function to get sheet data
def get_data():
    return sheet.get_all_records()

# Title
st.title("📋 Apexneura HR Panel")

# --- ADD COURSE ---
st.header("➕ Add Course")
course_name = st.text_input("Course Name")
course_time = st.text_input("Course Timing")
if st.button("Add Course"):
    if course_name and course_time:
        sheet.append_row([course_name, course_time, ""])
        st.success("✅ Course added successfully!")
    else:
        st.warning("⚠️ Please fill both Course Name and Course Timing.")

# --- ADD JOB OPENING ---
st.header("➕ Add Job Opening")
job_opening = st.text_input("Job Opening")
if st.button("Add Job Opening"):
    if job_opening:
        sheet.append_row(["", "", job_opening])
        st.success("✅ Job Opening added successfully!")
    else:
        st.warning("⚠️ Please enter a Job Opening.")

# --- DELETE COURSE ---
st.header("🗑️ Delete Course")
data = get_data()
courses = [row["Course Name"] for row in data if row["Course Name"]]
if courses:
    course_to_delete = st.selectbox("Select a course to delete", courses)
    if st.button("Delete Course"):
        for i, row in enumerate(data, start=2):  # row 1 is header
            if row["Course Name"] == course_to_delete:
                sheet.delete_row(i)
                st.success(f"✅ Deleted course: {course_to_delete}")
                st.experimental_rerun()
else:
    st.info("ℹ️ No courses available to delete.")

# --- DELETE JOB OPENING ---
st.header("🗑️ Delete Job Opening")
jobs = [row["Job Opening"] for row in data if row["Job Opening"]]
if jobs:
    job_to_delete = st.selectbox("Select a job to delete", jobs)
    if st.button("Delete Job Opening"):
        for i, row in enumerate(data, start=2):
            if row["Job Opening"] == job_to_delete:
                sheet.delete_row(i)
                st.success(f"✅ Deleted job: {job_to_delete}")
                st.experimental_rerun()
else:
    st.info("ℹ️ No job openings available to delete.")

# --- DELETE COURSE TIMING ---
st.header("🗑️ Delete Course Timing")
timings = [row["Course Timing"] for row in data if row["Course Timing"]]
if timings:
    timing_to_delete = st.selectbox("Select course timing to delete", timings)
    if st.button("Delete Course Timing"):
        for i, row in enumerate(data, start=2):
            if row["Course Timing"] == timing_to_delete:
                sheet.delete_row(i)
                st.success(f"✅ Deleted timing: {timing_to_delete}")
                st.experimental_rerun()
else:
    st.info("ℹ️ No course timings available to delete.")
