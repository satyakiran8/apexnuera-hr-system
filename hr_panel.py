import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)
sheet = client.open("apexneura_data").sheet1

# Fetch all data
def get_data():
    return sheet.get_all_records()

# Delete function with correct row number
def delete_entry(column_name, selected_value):
    data = get_data()
    for idx, row in enumerate(data):
        if row[column_name].strip().lower() == selected_value.strip().lower():
            sheet.delete_row(idx + 2)  # +2 because header = row 1 and data index starts from 0
            return True
    return False

st.title("\ud83d\udccb Apexneura HR Panel")

# ---------------- ADD COURSE ----------------
st.subheader("\u2795 Add Course")
course = st.text_input("Course Name")
timing = st.text_input("Course Timing")

if st.button("Add Course"):
    if course and timing:
        sheet.append_row([course, timing, ""])
        st.success("\u2705 Course added.")
    else:
        st.warning("\u26a0\ufe0f Please fill both fields.")

# ---------------- ADD JOB ----------------
st.subheader("\u2795 Add Job Opening")
job = st.text_input("Job Opening")

if st.button("Add Job"):
    if job:
        sheet.append_row(["", "", job])
        st.success("\u2705 Job opening added.")
    else:
        st.warning("\u26a0\ufe0f Enter a job opening.")

# ---------------- DELETE COURSE ----------------
st.subheader("\ud83d\uddd1\ufe0f Delete Course")
data = get_data()
courses = [row["Course Name"] for row in data if row["Course Name"]]

if courses:
    selected_course = st.selectbox("Select course to delete", courses)
    if st.button("Delete Course"):
        if delete_entry("Course Name", selected_course):
            st.success(f"\u2705 Deleted course: {selected_course}")
            st.experimental_rerun()
        else:
            st.error("\u274c Could not delete. Course not found.")

# ---------------- DELETE JOB ----------------
st.subheader("\ud83d\uddd1\ufe0f Delete Job Opening")
jobs = [row["Job Opening"] for row in data if row["Job Opening"]]

if jobs:
    selected_job = st.selectbox("Select job to delete", jobs)
    if st.button("Delete Job"):
        if delete_entry("Job Opening", selected_job):
            st.success(f"\u2705 Deleted job: {selected_job}")
            st.experimental_rerun()
        else:
            st.error("\u274c Could not delete. Job not found.")

# ---------------- DELETE TIMING ----------------
st.subheader("\ud83d\uddd1\ufe0f Delete Course Timing")
timings = [row["Course Timing"] for row in data if row["Course Timing"]]

if timings:
    selected_timing = st.selectbox("Select timing to delete", timings)
    if st.button("Delete Timing"):
        if delete_entry("Course Timing", selected_timing):
            st.success(f"\u2705 Deleted timing: {selected_timing}")
            st.experimental_rerun()
        else:
            st.error("\u274c Could not delete. Timing not found.")
