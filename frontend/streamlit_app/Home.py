import streamlit as st
import sys
import traceback

# Set page config FIRST
st.set_page_config(
    page_title="Debug Mode - Smart Attendance",
    page_icon="🔍",
    layout="wide"
)

# Debug info at the VERY TOP
st.write("🔍 **DEBUG MODE**")
st.write(f"Python version: {sys.version}")
st.write(f"Streamlit version: {st.__version__}")

try:
    # Your imports
    st.write("✅ Attempting imports...")
    import pandas as pd
    st.write("✅ pandas imported")
    import numpy as np
    st.write("✅ numpy imported")
    import plotly.graph_objects as go
    st.write("✅ plotly imported")
    
    st.success("✅ All imports successful!")
    
    # Simple UI
    st.title("🎓 University of Embu")
    st.markdown("### Smart Attendance System")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Students", "3,250")
        if st.button("👨‍🎓 Student Portal"):
            st.switch_page("pages/01_Student_Portal.py")
    with col2:
        st.metric("Today's Attendance", "2,450")
        if st.button("👨‍🏫 Lecturer Portal"):
            st.switch_page("pages/02_Lecturer_Portal.py")
            
except Exception as e:
    st.error(f"❌ ERROR: {str(e)}")
    st.code(traceback.format_exc())
