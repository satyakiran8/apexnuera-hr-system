import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set up Google Sheets connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)
sheet = client.open("apexnuera_data").sheet1

# Helper to get all rows
def get_all_data():
    return sheet.get_all_records()

# Title
st.title("Apexnuera HR Panel")

# --- Add Course Section ---
st.subheader("📘 Add Course")
course_name = st.text_input("Course Name")
course_timing = st.text_input("Course Timing")
if st.button("Add Course"):
    sheet.append_row([course_name, course_timing, ""])
    st.success("✅ Course added successfully!")

# --- Add Job Section ---
st.subheader("➕ Add Job Opening")
job_opening = st.text_input("Job Opening")
if st.button("Add Job Opening"):
    sheet.append_row(["", "", job_opening])
    st.success("✅ Job added successfully!")

# --- Delete Course ---
st.subheader("🗑️ Delete Course")
if st.checkbox("Show and delete courses"):
    data = get_all_data()
    course_list = list({row['Course Name'] for row in data if row['Course Name']})
    selected_course = st.selectbox("Select course to delete", course_list)
    if st.button("Delete Selected Course"):
        confirm = st.radio("Are you sure?", ["No", "Yes"])
        if confirm == "Yes":
            for i, row in enumerate(data, start=2):
                if row['Course Name'] == selected_course:
                    sheet.delete_row(i)
                    st.success("✅ Course deleted.")
                    break

# --- Delete Job Opening ---
st.subheader("🗑️ Delete Job Opening")
if st.checkbox("Show and delete job openings"):
    data = get_all_data()
    job_list = list({row['Job Opening'] for row in data if row['Job Opening']})
    selected_job = st.selectbox("Select job to delete", job_list)
    if st.button("Delete Selected Job Opening"):
        confirm = st.radio("Are you sure?", ["No", "Yes"])
        if confirm == "Yes":
            for i, row in enumerate(data, start=2):
                if row['Job Opening'] == selected_job:
                    sheet.delete_row(i)
                    st.success("✅ Job deleted.")
                    break

# --- Delete Course Timing ---
st.subheader("🗑️ Delete Course Timing")
if st.checkbox("Show and delete course timings"):
    data = get_all_data()
    timing_list = list({row['Course Timing'] for row in data if row['Course Timing']})
    selected_timing = st.selectbox("Select timing to delete", timing_list)
    if st.button("Delete Selected Course Timing"):
        confirm = st.radio("Are you sure?", ["No", "Yes"])
        if confirm == "Yes":
            for i, row in enumerate(data, start=2):
                if row['Course Timing'] == selected_timing:
                    sheet.delete_row(i)
                    st.success("✅ Timing deleted.")
                    break
