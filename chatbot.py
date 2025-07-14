import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fuzzywuzzy import fuzz
import pandas as pd

st.set_page_config(page_title="Apexnuera Chatbot", page_icon="🤖")

st.title("🤖 Apexnuera HR Chatbot")

# Connect to Google Sheet
def load_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open("apexnuera_data").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

df = load_sheet()

# Helper function: classify intent
def detect_intent(user_input):
    user_input = user_input.lower()
    course_keywords = ["course", "learning", "classes", "subjects", "training"]
    job_keywords = ["job", "hiring", "openings", "position", "career"]
    timing_keywords = ["timing", "time", "schedule", "when"]

    for word in course_keywords:
        if fuzz.partial_ratio(user_input, word) > 80:
            return "course"
    for word in job_keywords:
        if fuzz.partial_ratio(user_input, word) > 80:
            return "job"
    for word in timing_keywords:
        if fuzz.partial_ratio(user_input, word) > 80:
            return "timing"
    return "unknown"

# Chat loop
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Input
user_input = st.chat_input("Ask me about courses, jobs, or timings...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    intent = detect_intent(user_input)

    if intent == "course":
        courses = df["Course Name"].dropna().unique()
        reply = "**📘 Available Courses:**\n- " + "\n- ".join(courses)
    elif intent == "job":
        jobs = df["Job Opening"].dropna().unique()
        reply = "**💼 Current Job Openings:**\n- " + "\n- ".join(jobs)
    elif intent == "timing":
        timings = df["Course Timing"].dropna().unique()
        reply = "**🕒 Course Timings:**\n- " + "\n- ".join(timings)
    else:
        reply = "I'm not sure what you meant. You can ask me about **courses**, **job openings**, or **timings**."

    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})