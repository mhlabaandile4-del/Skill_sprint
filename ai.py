import google.generativeai as genai
import streamlit as st

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")


def ask_ai(prompt):
    response = model.generate_content(prompt)
    return response.text