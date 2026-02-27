"""Entry point for Streamlit Cloud deployment."""
import os
import sys

# Add frontend path
frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "streamlit_app")
sys.path.insert(0, frontend_path)

# Change to frontend directory
os.chdir(frontend_path)

# Direct import
import Home
