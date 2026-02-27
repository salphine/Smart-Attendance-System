import streamlit as st
import sys

st.set_page_config(page_title="Debug App", page_icon="✅")
st.title("✅ Debug Mode - If you see this, the app works!")
st.write(f"Python version: {sys.version}")
st.write(f"Streamlit version: {st.__version__}")
st.success("Core Streamlit is functional.")
