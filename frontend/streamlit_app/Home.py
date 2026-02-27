import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time

# Page config - MUST be first
st.set_page_config(
    page_title="University of Embu - Smart Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for animations and styling
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
    
    /* Glassmorphism Header */
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 40px;
        margin: 20px 0 30px 0;
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
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Live Indicator */
    .live-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(220, 53, 69, 0.3);
        backdrop-filter: blur(5px);
        padding: 8px 20px;
        border-radius: 50px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.3);
        animation: pulse 2s infinite;
    }
    
    .pulse-dot {
        width: 12px;
        height: 12px;
        background: #ff4444;
        border-radius: 50%;
        margin-right: 10px;
        animation: pulse-dot 1.5s infinite;
        box-shadow: 0 0 10px #ff4444;
    }
    
    @keyframes pulse-dot {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.3); opacity: 0.7; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Metric Cards */
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
    }
    
    .metric-value {
        font-size: 2.8em;
        font-weight: 700;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-change {
        font-size: 0.9em;
        padding: 5px 15px;
        border-radius: 25px;
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Chart Containers */
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
        margin-bottom: 15px;
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
        padding: 35px 25px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        cursor: pointer;
        animation: fadeInUp 0.9s ease;
        height: 100%;
    }
    
    .portal-card:hover {
        transform: translateY(-10px) scale(1.02);
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    .portal-icon {
        font-size: 4em;
        margin-bottom: 15px;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .portal-title {
        font-size: 2em;
        font-weight: 700;
        color: white;
        margin-bottom: 10px;
    }
    
    .portal-description {
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 20px;
        line-height: 1.6;
    }
    
    /* Activity Feed */
    .activity-item {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        border-left: 4px solid;
        padding: 12px 15px;
        margin: 8px 0;
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
</style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "home"

# Initialize session state for real-time data
if "analytics_data" not in st.session_state:
    st.session_state.analytics_data = {
        "total_students": 3250,
        "active_students": 2890,
        "total_staff": 145,
        "total_courses": 78,
        "today_attendance": random.randint(2400, 2800),
        "avg_attendance": 87.5,
        "system_uptime": datetime.now(),
        "verification_success": 98.2,
        "active_sessions": random.randint(18, 32),
        "last_updated": datetime.now()
    }

if "recent_activity" not in st.session_state:
    st.session_state.recent_activity = []

if "attendance_trend" not in st.session_state:
    # Generate 24 hours of data
    hours = [(datetime.now() - timedelta(hours=i)).strftime('%H:00') for i in range(24, 0, -1)]
    st.session_state.attendance_trend = {
        "hours": hours,
        "values": [random.randint(50, 200) for _ in range(24)]
    }

# Navigation function
def go_to(page):
    st.session_state.page = page
    st.rerun()

# Page routing
if st.session_state.page == "student":
    st.switch_page("pages/01_Student_Portal.py")
elif st.session_state.page == "lecturer":
    st.switch_page("pages/02_Lecturer_Portal.py")
else:
    # HOME PAGE CONTENT
    
    # Update real-time data
    def update_realtime_data():
        st.session_state.analytics_data["today_attendance"] = random.randint(2400, 2800)
        st.session_state.analytics_data["active_sessions"] = random.randint(18, 32)
        st.session_state.analytics_data["verification_success"] = round(98.2 + random.uniform(-0.8, 0.8), 1)
        st.session_state.analytics_data["last_updated"] = datetime.now()
        
        # Add random activity
        activities = [
            ("✅ Student verified: John Doe", "success"),
            ("🔄 Liveness check passed", "info"),
            ("📸 Face captured: Camera 3", "info"),
            ("⚠️ Multiple faces detected", "warning"),
            ("✅ Attendance marked: CS101", "success"),
            ("🆕 New session started: Lab 301", "info"),
            ("📊 Report generated", "info"),
            ("✅ 50 students marked present", "success")
        ]
        
        if random.random() > 0.4:
            activity_text, activity_type = random.choice(activities)
            st.session_state.recent_activity.insert(0, {
                'time': datetime.now().strftime('%H:%M:%S'),
                'text': activity_text,
                'type': activity_type
            })
            st.session_state.recent_activity = st.session_state.recent_activity[:8]
        
        # Update trend (shift and add new value)
        st.session_state.attendance_trend["values"].pop(0)
        st.session_state.attendance_trend["values"].append(random.randint(50, 200))

    # Call update (this will run on every rerun)
    update_realtime_data()

    # Header with live indicator
    st.markdown(f"""
    <div class="main-header">
        <div class="live-badge">
            <span class="pulse-dot"></span>
            <span>LIVE SYSTEM • REAL-TIME UPDATES • {datetime.now().strftime('%H:%M:%S')}</span>
        </div>
        <h1>🎓 University of Embu</h1>
        <h3>Smart Attendance System with AI-Powered Anti-Spoofing</h3>
        <p style="margin-top: 20px; opacity: 0.9;">{datetime.now().strftime('%A, %B %d, %Y')}</p>
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

    # Charts Row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Real-time Attendance (Last 24 Hours)</div>', unsafe_allow_html=True)
        
        # Create attendance trend chart
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=st.session_state.attendance_trend["hours"][-12:],
            y=st.session_state.attendance_trend["values"][-12:],
            mode='lines+markers',
            name='Students per hour',
            line=dict(color='#ffffff', width=3),
            fill='tozeroy',
            fillcolor='rgba(255, 255, 255, 0.1)'
        ))
        
        fig_trend.update_layout(
            xaxis_title="Time",
            yaxis_title="Number of Students",
            hovermode='x unified',
            showlegend=False,
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig_trend, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔴 Live Activity Feed</div>', unsafe_allow_html=True)
        
        if st.session_state.recent_activity:
            for activity in st.session_state.recent_activity:
                if activity['type'] == 'success':
                    border_color = "#4CAF50"
                elif activity['type'] == 'warning':
                    border_color = "#FFC107"
                else:
                    border_color = "#17a2b8"
                
                st.markdown(f"""
                <div class="activity-item" style="border-left-color: {border_color};">
                    <span>{activity['text']}</span>
                    <span style="font-size: 0.85em; opacity: 0.8;">{activity['time']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent activity")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Access Portals Section
    st.markdown("---")
    st.markdown("<h2 style='color: white; text-align: center; margin: 30px 0;'>🚀 Access Portals</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="portal-card">
            <div class="portal-icon">👨‍🎓</div>
            <div class="portal-title">Student Portal</div>
            <div class="portal-description">
                Mark attendance with AI-powered face recognition and anti-spoofing technology
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎓 Enter Student Portal", key="student_btn", width='stretch'):
            go_to("student")

    with col2:
        st.markdown("""
        <div class="portal-card">
            <div class="portal-icon">👨‍🏫</div>
            <div class="portal-title">Lecturer Portal</div>
            <div class="portal-description">
                Monitor attendance in real-time, view analytics, and manage courses
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📚 Enter Lecturer Portal", key="lecturer_btn", width='stretch'):
            go_to("lecturer")

    # Footer with auto-refresh info
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        uptime = datetime.now() - st.session_state.analytics_data['system_uptime']
        hours = uptime.total_seconds() / 3600
        st.markdown(f"""
        <div style="color: white; opacity: 0.8;">
            🟢 System uptime: {hours:.1f} hours
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="color: white; opacity: 0.8; text-align: center;">
            © 2026 University of Embu
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="color: white; opacity: 0.8; text-align: right;">
            🔄 Last updated: {st.session_state.analytics_data['last_updated'].strftime('%H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)

    # Auto-refresh every 5 seconds using a small trick
    if st.button("🔄 Refresh Data", key="refresh_btn"):
        st.rerun()


