"""Entry point for Streamlit Cloud deployment."""
import os
import sys
import streamlit as st

# Add the frontend path
frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "streamlit_app")
sys.path.insert(0, frontend_path)

# Change to the frontend directory
os.chdir(frontend_path)

# Import and run Home.py directly
import Home
