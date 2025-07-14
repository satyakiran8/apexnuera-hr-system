import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from openai import OpenAI
import re # Import re for more robust keyword matching

st.set_page_config(page_title="Apexnuera HR Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 Apexnuera HR Chatbot")

# --- Configuration & Secrets (IMPORTANT: Set these in .streamlit/secrets.toml) ---
# .streamlit/secrets.toml example:
# OPENAI_API_KEY="sk-your-openai-api-key-here"
# gcp_service_account = {
#     "type": "service_account",
#     "project_id": "your-gcp-project-id",
#     "private_key_id": "your-private-key-id",
#     "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
#     "client_email": "your-service-account-email@your-project-id.iam.gserviceaccount.com",
#     "client_id": "your-client-id",
#     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#     "token_uri": "https://oauth2.googleapis.com/token",
#     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email.iam.gserviceaccount.com",
#     "universe_domain": "googleapis.com"
# }
# ---------------------------------------------------------------------------------

# Initialize OpenAI client
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except AttributeError:
    st.error("OpenAI API key not found in Streamlit secrets. Please add it to your `.streamlit/secrets.toml` file.")
    st.stop() # Stop the app if API key is missing

# Connect to Google Sheet (using Streamlit's cache for performance)
@st.cache_data(ttl=3600) # Cache data for 1 hour to reduce API calls to Google Sheet
def load_sheet():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], scope
        )
        client_gspread = gspread.authorize(creds)
        sheet = client_gspread.open("apexnuera_data").sheet1 # Assumes your data is in the first sheet
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Failed to load data from Google Sheet. Please check your `gcp_service_account` secrets and sheet name. Error: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

df = load_sheet()

# Function to get specific data from the DataFrame based on keywords
def get_specific_data(user_input, dataframe):
    user_input_lower = user_input.lower()

    # Define keyword patterns for better matching
    course_pattern = r"\b(course|learning|classes|subjects|training|program)\b"
    job_pattern = r"\b(job|hiring|openings|position|career|employment)\b"
    timing_pattern = r"\b(timing|time|schedule|when|hours)\b"

    # Check for course related queries
    if re.search(course_pattern, user_input_lower):
        courses = dataframe["Course Name"].dropna().unique()
        if courses.size > 0:
            return "course", "**📘 Available Courses:**\n- " + "\n- ".join(courses)
        else:
            return "course", "I don't have information about specific courses right now. Please check back later or ask a general question."

    # Check for job related queries
    if re.search(job_pattern, user_input_lower):
        jobs = dataframe["Job Opening"].dropna().unique()
        if jobs.size > 0:
            return "job", "**💼 Current Job Openings:**\n- " + "\n- ".join(jobs)
        else:
            return "job", "I don't have information about specific job openings right now. Please check back later or ask a general question."

    # Check for timing related queries
    if re.search(timing_pattern, user_input_lower):
        timings = dataframe["Course Timing"].dropna().unique()
        if timings.size > 0:
            return "timing", "**🕒 Course Timings:**\n- " + "\n- ".join(timings)
        else:
            return "timing", "I don't have information about specific course timings right now. Please check back later or ask a general question."

    return "general", None # No specific data found for these keywords

# --- Chat Loop ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your Apexnuera HR Chatbot. How can I assist you today? You can ask me about **courses**, **job openings**, or **general HR queries**. 😊"}
    ]

# Display messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Input from user
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
        # Emphasize that it's an HR chatbot for Apexnuera and to be helpful/informative.
        system_prompt = {
            "role": "system",
            "content": """You are Apexnuera's helpful and professional HR Chatbot. Your primary goal is to assist users with their inquiries in a friendly and informative manner.
            If a question is about specific 'courses', 'job openings', or 'timings', and you have **already stated** that you don't have specific data for them (e.g., "I don't have information about specific courses right now."), then provide a general helpful answer or suggest how the user might find that information (e.g., "You might want to check the official Apexnuera website or contact the HR department directly for the most up-to-date details.").
            For all other general HR-related questions, provide a clear and concise response based on your training data. Do not make up information.
            """
        }

        # Prepend the system prompt to the messages sent to the LLM
        messages_for_llm.insert(0, system_prompt)

        try:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # You can experiment with "gpt-4", "gpt-4o" for better quality/cost
                    messages=messages_for_llm,
                    temperature=0.6, # A bit less creative for HR context, but still flexible
                    max_tokens=300 # Limit response length to keep it concise
                )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"I apologize, but I'm having trouble connecting to the AI at the moment. Please try again shortly. (Error: {e})"
            st.error(reply) # Display error to user

    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
