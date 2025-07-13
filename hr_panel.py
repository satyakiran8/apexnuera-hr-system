
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Setup Google Sheet connection
def connect_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open("apexnuera_data").sheet1
    return sheet

sheet = connect_sheet()

st.title("📋 Apexneura HR Panel")

# --- Section 1: Add Course ---
st.subheader("➕ Add Course")
course_name = st.text_input("Course Name")
course_timing = st.text_input("Course Timing")

if st.button("Add Course"):
    if course_name and course_timing:
        sheet.append_row([course_name, course_timing, ""])
        st.success("✅ Course added successfully!")
    else:
        st.warning("⚠️ Please fill both course name and timing.")

# --- Section 2: Add Job Opening ---
st.subheader("➕ Add Job Opening")
job_opening = st.text_input("Job Opening")

if st.button("Add Job Opening"):
    if job_opening:
        sheet.append_row(["", "", job_opening])
        st.success("✅ Job opening added successfully!")
    else:
        st.warning("⚠️ Please enter a job opening.")

# --- Section 3: Delete Course ---
st.subheader("🗑️ Delete Course")
course_data = sheet.get_all_records()
course_list = [row['Course Name'] for row in course_data if row['Course Name']]

if st.checkbox("Show and delete courses"):
    selected_course = st.selectbox("Select a course to delete", course_list)
    if st.button("Delete Course"):
        confirm = st.radio("Are you sure you want to delete?", ("No", "Yes"))
        if confirm == "Yes":
            for i, row in enumerate(course_data, start=2):
                if row['Course Name'] == selected_course:
                    sheet.delete_row(i)
                    st.success(f"✅ Deleted course: {selected_course}")
                    st.experimental_rerun()

# --- Section 4: Delete Job Opening ---
st.subheader("🗑️ Delete Job Opening")
job_list = [row['Job Opening'] for row in course_data if row['Job Opening']]

if st.checkbox("Show and delete job openings"):
    selected_job = st.selectbox("Select a job opening to delete", job_list)
    if st.button("Delete Job Opening"):
        confirm = st.radio("Are you sure you want to delete this job?", ("No", "Yes"), key="job")
        if confirm == "Yes":
            for i, row in enumerate(course_data, start=2):
                if row['Job Opening'] == selected_job:
                    sheet.delete_row(i)
                    st.success(f"✅ Deleted job opening: {selected_job}")
                    st.experimental_rerun()

# --- Section 5: Delete Course Timing ---
st.subheader("🗑️ Delete Course Timing")
timing_list = [row['Course Timing'] for row in course_data if row['Course Timing']]

if st.checkbox("Show and delete course timings"):
    selected_timing = st.selectbox("Select a timing to delete", timing_list)
    if st.button("Delete Course Timing"):
        confirm = st.radio("Are you sure you want to delete this timing?", ("No", "Yes"), key="timing")
        if confirm == "Yes":
            for i, row in enumerate(course_data, start=2):
                if row['Course Timing'] == selected_timing:
                    sheet.delete_row(i)
                    st.success(f"✅ Deleted timing: {selected_timing}")
                    st.experimental_rerun()
