import streamlit as st
import os
import sys

# Add the frontend/streamlit_app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "frontend", "streamlit_app"))

# Import and run Home.py
with open(os.path.join("frontend", "streamlit_app", "Home.py"), "r", encoding="utf-8") as f:
    exec(f.read())
