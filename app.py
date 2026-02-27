import streamlit as st
import os
import sys

st.set_page_config(
    page_title="Smart Attendance System",
    page_icon="🎓",
    layout="wide"
)

# Health check
st.write("App is starting...")
st.write(f"Python version: {sys.version}")
st.write(f"Current directory: {os.getcwd()}")

try:
    # Try to import Home
    from frontend.streamlit_app import Home
    st.success("Home imported successfully!")
except Exception as e:
    st.error(f"Error importing Home: {str(e)}")

st.write("If you see this, Streamlit is working!")
