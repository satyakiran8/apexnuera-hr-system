import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Streamlit UI
st.title("Apexnuera HR Panel")

# Input fields
course = st.text_input("Enter Course Name")
opening = st.text_input("Enter Job Opening")
timing = st.text_input("Enter Course Timing")

# On Submit
if st.button("Submit"):
    try:
        # Define Google Sheets API scope
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        # Load credentials securely from secrets.toml
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], scope
        )

        # Authorize and open the sheet
        client = gspread.authorize(creds)
        sheet = client.open("apexnuera_data").sheet1  # name of your Google Sheet

        # Add new row to sheet
        sheet.append_row([course, opening, timing])
        st.success("✅ Data submitted successfully!")

    except Exception as e:
        st.error(f"❌ Error: {e}")
