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
st.write(f"Current directory: {__file__}")

try:
    # Test imports one by one
    st.write("📦 Testing imports...")
    
    st.write("  - Importing pandas...")
    import pandas as pd
    st.write("  ✅ pandas imported")
    
    st.write("  - Importing numpy...")
    import numpy as np
    st.write("  ✅ numpy imported")
    
    st.write("  - Importing plotly...")
    import plotly.graph_objects as go
    import plotly.express as px
    st.write("  ✅ plotly imported")
    
    st.write("  - Importing datetime...")
    from datetime import datetime, timedelta
    st.write("  ✅ datetime imported")
    
    st.write("  - Importing random...")
    import random
    st.write("  ✅ random imported")
    
    st.success("✅ All imports successful!")
    
    # Now try to render something simple
    st.title("🎓 University of Embu")
    st.markdown("### Smart Attendance System")
    
    # Simple metrics that definitely work
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Students", "3,250")
    with col2:
        st.metric("Today's Attendance", "2,450")
    
    # Simple button
    if st.button("Test Button"):
        st.balloons()
    
    st.write("---")
    st.write("✅ If you can see this, the basic app is working!")
    
except Exception as e:
    st.error(f"❌ ERROR: {type(e).__name__}: {str(e)}")
    st.code(traceback.format_exc())
