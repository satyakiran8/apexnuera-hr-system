import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)
sheet = client.open("apexnuera_data").sheet1

st.title("Apexnuera HR Panel")

st.header("Add Course, Timing & Job")

st.subheader("Add Course")
course = st.text_input("Course Name")
timing = st.text_input("Course Timing")

st.subheader("Add Job Opening")
job = st.text_input("Job Opening")

if st.button("Submit All"):
    if course and timing:
        sheet.append_row([course, timing, ""])
        st.success("Course added successfully")
    if job:
        sheet.append_row(["", "", job])
        st.success("Job opening added successfully")
    if not course and not timing and not job:
        st.warning("Please fill at least one section to submit.")
