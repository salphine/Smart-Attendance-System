import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time

# Page config
st.set_page_config(
    page_title="Lecturer Portal - University of Embu",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Professional Dashboard Styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Login Container */
    .login-container {
        background: white;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin: 50px auto;
        max-width: 450px;
    }
    
    /* Header */
    .lecturer-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Cards */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 5px solid;
        margin: 10px 0;
    }
    
    .stat-title {
        color: #666;
        font-size: 0.9em;
        text-transform: uppercase;
    }
    
    .stat-value {
        font-size: 2.2em;
        font-weight: 700;
        color: #333;
    }
    
    .course-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 10px 0;
        transition: transform 0.3s;
    }
    
    .course-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .badge-success {
        background: #d4edda;
        color: #155724;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
    }
    
    .badge-warning {
        background: #fff3cd;
        color: #856404;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
    }
    
    .badge-danger {
        background: #f8d7da;
        color: #721c24;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
    }
    
    .progress-container {
        background: #e9ecef;
        border-radius: 10px;
        height: 8px;
        width: 100%;
        margin: 10px 0;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transition: width 0.5s ease;
    }
    
    .live-badge {
        background: #dc3545;
        color: white;
        padding: 5px 15px;
        border-radius: 25px;
        font-size: 0.9em;
        font-weight: 600;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .action-btn {
        background: #667eea;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1em;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
        margin: 5px 0;
    }
    
    .action-btn:hover {
        background: #5a67d8;
        transform: translateY(-2px);
    }
    
    .data-table {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 10px 0;
    }
    
    .student-grid-item {
        background: white;
        border: 2px solid;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .student-grid-item:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'lecturer_logged_in' not in st.session_state:
    st.session_state.lecturer_logged_in = False
    st.session_state.lecturer_info = {}
    st.session_state.selected_course = None
    st.session_state.current_tab = "Dashboard"
    st.session_state.courses_data = {}
    st.session_state.live_attendance = []

# Initialize sample data on first load
if not st.session_state.courses_data:
    # Sample courses
    st.session_state.courses_data = {
        'CS301': {
            'name': 'Data Structures and Algorithms',
            'students': 75,
            'schedule': 'Mon/Wed 10:00-12:00',
            'room': 'LT101',
            'attendance_today': random.randint(45, 70),
            'avg_attendance': 85.5,
            'students_list': []
        },
        'CS401': {
            'name': 'Machine Learning',
            'students': 60,
            'schedule': 'Tue/Thu 14:00-16:00',
            'room': 'LT203',
            'attendance_today': random.randint(35, 55),
            'avg_attendance': 78.3,
            'students_list': []
        },
        'CS202': {
            'name': 'Database Systems',
            'students': 85,
            'schedule': 'Wed/Fri 09:00-11:00',
            'room': 'LT105',
            'attendance_today': random.randint(50, 80),
            'avg_attendance': 82.1,
            'students_list': []
        }
    }
    
    # Generate sample students for each course
    first_names = ['John', 'Mary', 'Peter', 'Sarah', 'David', 'Lucy', 'James', 'Grace', 'Paul', 'Esther',
                   'Michael', 'Alice', 'Robert', 'Jane', 'William', 'Catherine', 'Joseph', 'Ruth', 'Daniel', 'Hannah']
    last_names = ['Kamau', 'Wanjiku', 'Odhiambo', 'Akinyi', 'Mwangi', 'Njeri', 'Omondi', 'Atieno', 'Kipchoge', 'Chebet',
                  'Ochieng', 'Wambui', 'Kiprop', 'Achieng', 'Mutua', 'Nduku', 'Kariuki', 'Wairimu', 'Kipkorir', 'Jeruto']
    
    for course_code in st.session_state.courses_data:
        students = []
        for i in range(st.session_state.courses_data[course_code]['students']):
            student = {
                'id': f'REG{2024000 + i}',
                'name': f"{random.choice(first_names)} {random.choice(last_names)}",
                'email': f"student{i}@students.embu.ac.ke",
                'attendance_percentage': random.randint(60, 100),
                'last_attendance': (datetime.now() - timedelta(days=random.randint(0, 5))).strftime('%Y-%m-%d'),
                'status': random.choice(['active', 'active', 'active', 'at-risk', 'active']),
                'face_registered': random.choice([True, True, True, True, False])
            }
            students.append(student)
        st.session_state.courses_data[course_code]['students_list'] = students

# Login Page
if not st.session_state.lecturer_logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: white;"> Lecturer Portal</h1>
            <p style="color: white; opacity: 0.9;">University of Embu - Smart Attendance System</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #333;">Welcome Back</h2>
            <p style="color: #666;">Please login to access your dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            staff_id = st.text_input("Staff ID", placeholder="Enter your staff ID")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                remember = st.checkbox("Remember me")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Login to Dashboard")
            
            if submitted:
                if staff_id and password:
                    # Simple authentication for demo
                    st.session_state.lecturer_logged_in = True
                    st.session_state.lecturer_info = {
                        'id': staff_id,
                        'name': 'Prof. John Omondi',
                        'department': 'Computer Science',
                        'faculty': 'Faculty of Science & Technology',
                        'email': f'{staff_id}@embu.ac.ke',
                        'courses': ['CS301', 'CS401', 'CS202']
                    }
                    st.rerun()
                else:
                    st.error("Please enter both Staff ID and Password")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <p style="color: #999; font-size: 0.9em;">Demo Login: Use any credentials</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Dashboard (Logged In)
else:
    # Header with Lecturer Info
    st.markdown(f"""
    <div class="lecturer-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1>Welcome, {st.session_state.lecturer_info['name']} </h1>
                <h3>{st.session_state.lecturer_info['department']} | {st.session_state.lecturer_info['faculty']}</h3>
                <p style="margin-top: 10px; opacity: 0.9;">{st.session_state.lecturer_info['email']}</p>
            </div>
            <div style="text-align: right;">
                <span class="live-badge"> LIVE DASHBOARD</span>
                <p style="margin-top: 10px;">{datetime.now().strftime('%A, %B %d, %Y')}<br>{datetime.now().strftime('%H:%M:%S')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #333;">{st.session_state.lecturer_info['name']}</h3>
            <p style="color: #666;">{st.session_state.lecturer_info['id']}</p>
            <hr>
            <p style="color: #666;"> {st.session_state.lecturer_info['email']}</p>
            <p style="color: #666;"> {st.session_state.lecturer_info['faculty']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("###  Navigation")
        
        tabs = ["Dashboard", "My Courses", "Students", "Attendance", "Analytics", "Settings"]
        selected_tab = st.radio("Navigation", tabs, index=0, label_visibility="collapsed")
        st.session_state.current_tab = selected_tab
        
        st.markdown("---")
        
        # Quick Stats
        total_students = sum(course['students'] for course in st.session_state.courses_data.values())
        total_present = sum(course['attendance_today'] for course in st.session_state.courses_data.values())
        
        st.markdown("###  Quick Stats")
        st.metric("Total Students", total_students)
        st.metric("Present Today", total_present)
        st.metric("Attendance Rate", f"{(total_present/total_students*100):.1f}%")
        
        st.markdown("---")
        
        if st.button(" Logout"):
            st.session_state.lecturer_logged_in = False
            st.rerun()
    
    # Main Content Area based on selected tab
    if st.session_state.current_tab == "Dashboard":
        st.markdown("###  Dashboard Overview")
        
        # Summary Cards
        col1, col2, col3, col4 = st.columns(4)
        
        total_students = sum(course['students'] for course in st.session_state.courses_data.values())
        total_present = sum(course['attendance_today'] for course in st.session_state.courses_data.values())
        avg_attendance = np.mean([course['avg_attendance'] for course in st.session_state.courses_data.values()])
        
        at_risk_students = 0
        for course in st.session_state.courses_data.values():
            at_risk_students += sum(1 for s in course['students_list'] if s['status'] == 'at-risk')
        
        with col1:
            st.markdown(f"""
            <div class="stat-card" style="border-left-color: #667eea;">
                <div class="stat-title">Total Students</div>
                <div class="stat-value">{total_students}</div>
                <div style="color: #28a745;"> 12 this semester</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card" style="border-left-color: #48bb78;">
                <div class="stat-title">Present Today</div>
                <div class="stat-value">{total_present}</div>
                <div style="color: #28a745;">{(total_present/total_students*100):.1f}% attendance</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card" style="border-left-color: #fbbf24;">
                <div class="stat-title">Avg Attendance</div>
                <div class="stat-value">{avg_attendance:.1f}%</div>
                <div style="color: #666;">this semester</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card" style="border-left-color: #f56565;">
                <div class="stat-title">At-Risk Students</div>
                <div class="stat-value">{at_risk_students}</div>
                <div style="color: #dc3545;">need attention</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            st.markdown("####  Weekly Attendance Trend")
            
            # Generate weekly data
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
            attendance_data = [random.randint(150, 200) for _ in days]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=days,
                y=attendance_data,
                mode='lines+markers',
                line=dict(color='#667eea', width=3),
                fill='tozeroy'
            ))
            fig.update_layout(
                height=300,
                margin=dict(l=40, r=40, t=20, b=40),
                yaxis_title="Students Present",
                showlegend=False
            )
            st.plotly_chart(fig)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            st.markdown("####  Course Distribution")
            
            courses = list(st.session_state.courses_data.keys())
            students = [c['students'] for c in st.session_state.courses_data.values()]
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=courses,
                    values=students,
                    hole=0.4,
                    marker_colors=['#667eea', '#48bb78', '#fbbf24']
                )
            ])
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Live Attendance Feed
        st.markdown("####  Live Attendance Feed")
        
        # Generate live updates
        if len(st.session_state.live_attendance) < 5:
            students = ['John Kamau', 'Mary Wanjiku', 'Peter Odhiambo', 'Sarah Akinyi', 'David Mwangi']
            for _ in range(3):
                st.session_state.live_attendance.append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'student': random.choice(students),
                    'course': random.choice(list(st.session_state.courses_data.keys())),
                    'status': random.choice([' Verified', ' Present', ' Verifying']),
                    'confidence': random.randint(92, 99)
                })
        
        for activity in st.session_state.live_attendance[-5:]:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.markdown(f"**{activity['student']}**")
            with col2:
                st.markdown(f"*{activity['course']}*")
            with col3:
                st.markdown(f"{activity['status']}")
            with col4:
                st.markdown(f"`{activity['confidence']}%`")
    
    elif st.session_state.current_tab == "My Courses":
        st.markdown("###  My Courses")
        
        # Course cards
        cols = st.columns(2)
        for idx, (code, course) in enumerate(st.session_state.courses_data.items()):
            with cols[idx % 2]:
                attendance_rate = (course['attendance_today'] / course['students']) * 100
                
                if attendance_rate >= 75:
                    badge = '<span class="badge-success">Good Attendance</span>'
                elif attendance_rate >= 50:
                    badge = '<span class="badge-warning">Moderate</span>'
                else:
                    badge = '<span class="badge-danger">Low Attendance</span>'
                
                st.markdown(f"""
                <div class="course-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>{code}: {course['name']}</h3>
                        {badge}
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0;">
                        <div> Students: {course['students']}</div>
                        <div> {course['schedule']}</div>
                        <div> Room: {course['room']}</div>
                        <div> Avg: {course['avg_attendance']}%</div>
                    </div>
                    <div style="margin: 15px 0;">
                        <div style="display: flex; justify-content: space-between;">
                            <span>Today's Attendance</span>
                            <span>{attendance_rate:.1f}%</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {attendance_rate}%;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    elif st.session_state.current_tab == "Students":
        st.markdown("###  Student Management")
        
        # Course selector
        selected_course = st.selectbox(
            "Select Course",
            options=list(st.session_state.courses_data.keys()),
            format_func=lambda x: f"{x} - {st.session_state.courses_data[x]['name']}"
        )
        
        if selected_course:
            course = st.session_state.courses_data[selected_course]
            students = course['students_list']
            
            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", len(students))
            with col2:
                active = sum(1 for s in students if s['status'] == 'active')
                st.metric("Active", active)
            with col3:
                at_risk = sum(1 for s in students if s['status'] == 'at-risk')
                st.metric("At-Risk", at_risk)
            with col4:
                registered = sum(1 for s in students if s['face_registered'])
                st.metric("Face Registered", f"{registered}/{len(students)}")
            
            # Search
            search = st.text_input(" Search students", placeholder="Name or ID...")
            
            # Display students table
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            
            filtered_students = students
            if search:
                filtered_students = [s for s in students if 
                                   search.lower() in s['name'].lower() or 
                                   search.lower() in s['id'].lower()]
            
            if filtered_students:
                df = pd.DataFrame(filtered_students)
                st.dataframe(
                    df[['id', 'name', 'attendance_percentage', 'status', 'last_attendance', 'face_registered']],
                    hide_index=True,
                    column_config={
                        'attendance_percentage': st.column_config.ProgressColumn(
                            "Attendance %",
                            min_value=0,
                            max_value=100,
                            format="%d%%"
                        ),
                        'face_registered': st.column_config.CheckboxColumn("Face Reg")
                    }
                )
            else:
                st.info("No students found")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_tab == "Attendance":
        st.markdown("###  Live Attendance Monitoring")
        
        # Course selector
        selected_course = st.selectbox(
            "Select Course",
            options=list(st.session_state.courses_data.keys()),
            format_func=lambda x: f"{x} - {st.session_state.courses_data[x]['name']}",
            key="attendance_course"
        )
        
        if selected_course:
            course = st.session_state.courses_data[selected_course]
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Present Now", course['attendance_today'])
            with col2:
                st.metric("Total Students", course['students'])
            with col3:
                percentage = (course['attendance_today'] / course['students']) * 100
                st.metric("Attendance Rate", f"{percentage:.1f}%")
            
            # Controls
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button(" Start Session"):
                    st.success("Session started!")
            with col2:
                if st.button(" Pause"):
                    st.warning("Session paused")
            with col3:
                if st.button(" End"):
                    st.info("Session ended")
            with col4:
                if st.button(" Refresh"):
                    st.rerun()
            
            # Student grid
            st.markdown("#### Student Status Grid")
            cols = st.columns(5)
            for idx, student in enumerate(course['students_list'][:20]):
                with cols[idx % 5]:
                    status = random.choice(['present', 'absent', 'verifying'])
                    
                    if status == 'present':
                        bg = "#d4edda"
                        border = "#28a745"
                        text = ""
                    elif status == 'verifying':
                        bg = "#fff3cd"
                        border = "#ffc107"
                        text = ""
                    else:
                        bg = "#f8d7da"
                        border = "#dc3545"
                        text = ""
                    
                    st.markdown(f"""
                    <div style="background: {bg}; border: 2px solid {border}; 
                                border-radius: 10px; padding: 10px; margin: 5px; text-align: center;">
                        <div style="font-weight: 600;">{student['name'].split()[0]}</div>
                        <div>{text}</div>
                        <div style="font-size: 0.8em;">{student['id'][-4:]}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    elif st.session_state.current_tab == "Analytics":
        st.markdown("###  Advanced Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            st.markdown("####  Attendance Trends")
            
            # Generate trend data
            weeks = [f"Week {i}" for i in range(1, 9)]
            trend_data = []
            for course in st.session_state.courses_data.values():
                trend_data.append({
                    'name': course['name'][:15] + '...',
                    'values': [random.randint(70, 95) for _ in weeks]
                })
            
            fig = go.Figure()
            for data in trend_data:
                fig.add_trace(go.Scatter(
                    x=weeks,
                    y=data['values'],
                    mode='lines+markers',
                    name=data['name']
                ))
            
            fig.update_layout(height=400, hovermode='x unified')
            st.plotly_chart(fig)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            st.markdown("####  Performance Comparison")
            
            courses = list(st.session_state.courses_data.keys())
            attendance = [c['avg_attendance'] for c in st.session_state.courses_data.values()]
            
            fig = go.Figure(data=[
                go.Bar(x=courses, y=attendance, marker_color=['#667eea', '#48bb78', '#fbbf24'])
            ])
            fig.update_layout(
                height=400,
                yaxis_title="Attendance %",
                yaxis_range=[0, 100]
            )
            st.plotly_chart(fig)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # At-risk analysis
        st.markdown("####  At-Risk Students Analysis")
        
        risk_data = []
        for code, course in st.session_state.courses_data.items():
            at_risk = sum(1 for s in course['students_list'] if s['attendance_percentage'] < 75)
            risk_data.append({
                'Course': code,
                'At-Risk': at_risk,
                'Total': course['students'],
                'Percentage': (at_risk / course['students']) * 100
            })
        
        df_risk = pd.DataFrame(risk_data)
        st.dataframe(df_risk, hide_index=True)
    
    elif st.session_state.current_tab == "Settings":
        st.markdown("###  Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("####  Profile Settings")
            with st.form("profile_form"):
                name = st.text_input("Full Name", value=st.session_state.lecturer_info['name'])
                email = st.text_input("Email", value=st.session_state.lecturer_info['email'])
                dept = st.text_input("Department", value=st.session_state.lecturer_info['department'])
                
                st.markdown("####  Change Password")
                current = st.text_input("Current Password", type="password")
                new = st.text_input("New Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Update Profile"):
                    st.success("Profile updated successfully!")
        
        with col2:
            st.markdown("####  Notification Preferences")
            
            prefs = {
                "Email Notifications": True,
                "SMS Alerts": False,
                "Daily Attendance Reports": True,
                "Weekly Analytics": True,
                "At-Risk Alerts": True,
                "System Updates": False
            }
            
            for pref, value in prefs.items():
                st.checkbox(pref, value=value)
            
            st.markdown("####  Session Settings")
            duration = st.slider("Default Session Duration (minutes)", 30, 180, 60)
            auto_end = st.checkbox("Auto-end sessions", value=True)
            
            if st.button("Save Settings"):
                st.success("Settings saved!")






