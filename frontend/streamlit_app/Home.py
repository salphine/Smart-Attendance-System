import streamlit as st
import time

# Must be the absolute first Streamlit command
st.set_page_config(
    page_title="University of Embu",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Simple state initialization
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
    # Simple home page
    st.title("🎓 University of Embu")
    st.subheader("Smart Attendance System")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Student Portal", use_container_width=True):
            go_to("student")
    with col2:
        if st.button("Lecturer Portal", use_container_width=True):
            go_to("lecturer")
