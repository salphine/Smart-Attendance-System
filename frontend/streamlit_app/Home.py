import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="University of Embu - Smart Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to(page):
    st.session_state.page = page
    st.rerun()

# Page routing
if st.session_state.page == "student":
    st.switch_page("pages/01_Student_Portal.py")
elif st.session_state.page == "lecturer":
    st.switch_page("pages/02_Lecturer_Portal.py")
else:
    st.title("🎓 University of Embu")
    st.markdown("### Smart Attendance System")
    
    # Simple working buttons - NO width parameter at all
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎓 Enter Student Portal", key="student_btn"):
            go_to("student")
    with col2:
        if st.button("📚 Enter Lecturer Portal", key="lecturer_btn"):
            go_to("lecturer")
