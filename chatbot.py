import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from openai import OpenAI # Import OpenAI library

st.set_page_config(page_title="Apexnuera Chatbot", page_icon="🤖")

st.title("🤖 Apexnuera HR Chatbot")

# Initialize OpenAI client
# Ensure your OpenAI API key is in st.secrets["OPENAI_API_KEY"]
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except AttributeError:
    st.error("OpenAI API key not found in Streamlit secrets. Please add it to .streamlit/secrets.toml")
    st.stop() # Stop the app if API key is missing

# Connect to Google Sheet
@st.cache_data(ttl=3600) # Cache data for 1 hour to reduce API calls
def load_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope)
    client_gspread = gspread.authorize(creds)
    sheet = client_gspread.open("apexnuera_data").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

df = load_sheet()

# Function to get specific data from the DataFrame based on keywords
def get_specific_data(user_input, dataframe):
    user_input_lower = user_input.lower()
    
    # Check for course related queries
    course_keywords = ["course", "learning", "classes", "subjects", "training", "program"]
    if any(word in user_input_lower for word in course_keywords):
        courses = dataframe["Course Name"].dropna().unique()
        if courses.size > 0:
            return "course", "**📘 Available Courses:**\n- " + "\n- ".join(courses)
    
    # Check for job related queries
    job_keywords = ["job", "hiring", "openings", "position", "career", "employment"]
    if any(word in user_input_lower for word in job_keywords):
        jobs = dataframe["Job Opening"].dropna().unique()
        if jobs.size > 0:
            return "job", "**💼 Current Job Openings:**\n- " + "\n- ".join(jobs)
    
    # Check for timing related queries
    timing_keywords = ["timing", "time", "schedule", "when", "hours"]
    if any(word in user_input_lower for word in timing_keywords):
        timings = dataframe["Course Timing"].dropna().unique()
        if timings.size > 0:
            return "timing", "**🕒 Course Timings:**\n- " + "\n- ".join(timings)
            
    return "general", None # No specific data found for these keywords

# Chat loop
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your Apexnuera HR Chatbot. How can I assist you today? You can ask me about courses, job openings, or general HR queries. 😊"}
    ]

# Display messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Input
user_input = st.chat_input("Ask me anything...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # First, try to get specific data from the Google Sheet
    intent, specific_reply = get_specific_data(user_input, df)

    if specific_reply:
        reply = specific_reply
    else:
        # If no specific data found, send the conversation to the LLM
        messages_for_llm = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        
        # Add a system prompt to guide the LLM's behavior
        system_prompt = {
            "role": "system",
            "content": "You are a helpful HR chatbot for Apexnuera. Provide concise and relevant information. If a question is about courses, jobs, or timings, and you cannot find specific data in your internal knowledge, state that you do not have that specific information but try to provide a general helpful answer."
        }
        
        # Prepend the system prompt to the messages sent to the LLM
        messages_for_llm.insert(0, system_prompt)

        try:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Or "gpt-4", "gpt-4o", or a Gemini model (requires different client initialization)
                    messages=messages_for_llm,
                    temperature=0.7, # Adjust for creativity (0.0 for deterministic, 1.0 for very creative)
                    max_tokens=300 # Limit response length
                )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"An error occurred while connecting to the AI: {e}"
            st.error(reply)

    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
