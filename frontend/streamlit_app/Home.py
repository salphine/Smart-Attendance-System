import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
from streamlit_autorefresh import st_autorefresh

# Page config
st.set_page_config(
    page_title="University of Embu - Smart Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Animated Gradient Background */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Header with glassmorphism */
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 50px;
        margin: 30px 20px 40px 20px;
        text-align: center;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        animation: fadeInDown 1s ease;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main-header h1 {
        font-size: 3.5em;
        font-weight: 700;
        margin-bottom: 15px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header h3 {
        font-weight: 300;
        opacity: 0.95;
        font-size: 1.5em;
    }
    
    /* Live Indicator */
    .live-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(220, 53, 69, 0.3);
        backdrop-filter: blur(5px);
        padding: 10px 25px;
        border-radius: 50px;
        margin-bottom: 25px;
        border: 1px solid rgba(255,255,255,0.3);
        animation: pulse 2s infinite;
    }
    
    .pulse-dot {
        width: 14px;
        height: 14px;
        background: #ff4444;
        border-radius: 50%;
        margin-right: 12px;
        animation: pulse-dot 1.5s infinite;
        box-shadow: 0 0 10px #ff4444;
    }
    
    @keyframes pulse-dot {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.3); opacity: 0.7; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Metric Cards with glassmorphism */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        margin: 10px 0;
        animation: fadeInUp 0.5s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 10s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 15px 30px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        font-size: 1em;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
    }
    
    .metric-value {
        font-size: 2.8em;
        font-weight: 700;
        margin: 15px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
    }
    
    .metric-change {
        font-size: 0.9em;
        padding: 5px 15px;
        border-radius: 25px;
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        position: relative;
    }
    
    /* Chart Containers with glassmorphism */
    .chart-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 10px 0;
        color: white;
        animation: fadeInUp 0.7s ease;
    }
    
    .chart-title {
        font-size: 1.3em;
        font-weight: 600;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    /* Portal Cards */
    .portal-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 25px;
        padding: 40px 30px;
        width: 450px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        cursor: pointer;
        animation: fadeInUp 0.9s ease;
    }
    
    .portal-card:hover {
        transform: translateY(-15px) scale(1.02);
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    .portal-icon {
        font-size: 5em;
        margin-bottom: 20px;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .portal-title {
        font-size: 2.2em;
        font-weight: 700;
        color: white;
        margin-bottom: 15px;
    }
    
    .portal-description {
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 25px;
        line-height: 1.6;
        font-size: 1.1em;
    }
    
    .portal-stats {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
        padding: 15px;
        margin: 20px 0;
    }
    
    .stat-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        font-size: 1.1em;
    }
    
    .stat-row:last-child {
        border-bottom: none;
    }
    
    /* Activity Feed Items */
    .activity-item {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        border-left: 4px solid;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: slideInRight 0.5s ease;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Health Metric Cards */
    .health-metric {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin: 5px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s;
    }
    
    .health-metric:hover {
        transform: scale(1.05);
        background: rgba(255, 255, 255, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# Auto-refresh every 5 seconds
refresh_count = st_autorefresh(interval=10000, key="home_autorefresh")

# Initialize session state
if 'analytics_data' not in st.session_state:
    st.session_state.analytics_data = {
        'total_students': 3250,
        'active_students': 2890,
        'total_staff': 145,
        'total_courses': 78,
        'today_attendance': random.randint(2400, 2800),
        'avg_attendance': 87.5,
        'system_uptime': datetime.now(),
        'verification_success': 98.2,
        'active_sessions': random.randint(18, 32)
    }

# Header without emojis
st.markdown(f"""
<div class="main-header">
    <div class="live-badge">
        <span class="pulse-dot"></span>
        <span>LIVE SYSTEM - REAL-TIME UPDATES</span>
    </div>
    <h1>University of Embu</h1>
    <h3>Smart Attendance System with AI-Powered Anti-Spoofing</h3>
    <p style="margin-top: 20px; opacity: 0.9;">{datetime.now().strftime('%A, %B %d, %Y - %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

attendance_percentage = (st.session_state.analytics_data['today_attendance'] / 
                        st.session_state.analytics_data['total_students']) * 100

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">TOTAL STUDENTS</div>
        <div class="metric-value">{st.session_state.analytics_data['total_students']:,}</div>
        <div class="metric-change">↑ 124 this semester</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">TODAY'S ATTENDANCE</div>
        <div class="metric-value">{st.session_state.analytics_data['today_attendance']:,}</div>
        <div class="metric-change">{attendance_percentage:.1f}% of total</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">ACTIVE SESSIONS</div>
        <div class="metric-value">{st.session_state.analytics_data['active_sessions']}</div>
        <div class="metric-change">{st.session_state.analytics_data['total_courses']} total courses</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">VERIFICATION RATE</div>
        <div class="metric-value">{st.session_state.analytics_data['verification_success']}%</div>
        <div class="metric-change">99.9% anti-spoofing</div>
    </div>
    """, unsafe_allow_html=True)

# Access Portals Section
st.markdown("---")
st.markdown("<h2 style='color: white; text-align: center; margin: 30px 0;'>Access Portals</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="portal-card">
        <div class="portal-icon">👨‍🎓</div>
        <div class="portal-title">Student Portal</div>
        <div class="portal-description">
            Advanced face recognition attendance with multi-layer anti-spoofing and real-time verification
        </div>
        <div class="portal-stats">
            <div class="stat-row">
                <span>Active Students</span>
                <span>2,345</span>
            </div>
            <div class="stat-row">
                <span>Today's Attendance</span>
                <span>1,890</span>
            </div>
            <div class="stat-row">
                <span>Verification Rate</span>
                <span>98.5%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Enter Student Portal", key="student_btn", use_container_width=True):
        st.switch_page("pages/01_Student_Portal.py")

with col2:
    st.markdown("""
    <div class="portal-card">
        <div class="portal-icon">👨‍🏫</div>
        <div class="portal-title">Lecturer Portal</div>
        <div class="portal-description">
           Salphine chemos Professional dashboard with real-time monitoring, predictive analytics, and student management
        </div>
        <div class="portal-stats">
            <div class="stat-row">
                <span>Active Lecturers</span>
                <span>78</span>
            </div>
            <div class="stat-row">
                <span>Active Courses</span>
                <span>45</span>
            </div>
            <div class="stat-row">
                <span>Live Sessions</span>
                <span>23</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Enter Lecturer Portal", key="lecturer_btn", use_container_width=True):
        st.switch_page("pages/02_Lecturer_Portal.py")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="color: white; opacity: 0.8;">
        Auto-refresh: {refresh_count} updates
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="color: white; opacity: 0.8; text-align: center;">
        © 2026 University of Embu - Salphine Chemos Smart Attendance System
    </div>
    """, unsafe_allow_html=True)

with col3:
    uptime = datetime.now() - st.session_state.analytics_data['system_uptime']
    hours = uptime.total_seconds() / 3600
    st.markdown(f"""
    <div style="color: white; opacity: 0.8; text-align: right;">
        System uptime: {hours:.1f} hours
    </div>
    """, unsafe_allow_html=True)


