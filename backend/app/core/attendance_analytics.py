# backend/app/analytics/attendance_analytics.py
"""
Real-time analytics and insights generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import json

class AttendanceAnalytics:
    """
    Generate actionable insights from attendance data
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        
    def generate_real_time_dashboard(self, course_id: str, date: str) -> Dict:
        """
        Generate comprehensive real-time dashboard data
        """
        # Get today's attendance
        attendance_data = self._get_attendance_data(course_id, date)
        
        # Calculate metrics
        total_students = len(attendance_data)
        present_now = self._get_current_presence(course_id)
        
        dashboard = {
            'summary': {
                'total_students': total_students,
                'present_now': present_now,
                'absent': total_students - present_now,
                'attendance_rate': (present_now / total_students * 100) if total_students > 0 else 0,
                'last_updated': datetime.now().isoformat()
            },
            'trends': self._generate_attendance_trends(course_id),
            'heatmap': self._generate_seating_heatmap(course_id, date),
            'predictions': self._predict_attendance_trends(course_id),
            'alerts': self._generate_alerts(course_id, attendance_data)
        }
        
        return dashboard
    
    def _generate_attendance_trends(self, course_id: str) -> Dict:
        """
        Generate attendance trends over time
        """
        # Get last 30 days attendance
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        query = """
        SELECT date, COUNT(*) as present_count
        FROM attendance
        WHERE course_id = ? 
        AND date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        """
        
        results = self.db.execute(query, (course_id, start_date, end_date)).fetchall()
        
        dates = []
        counts = []
        
        for row in results:
            dates.append(row['date'])
            counts.append(row['present_count'])
        
        # Create trend chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=counts,
            mode='lines+markers',
            name='Attendance',
            line=dict(color='#48bb78', width=3)
        ))
        
        fig.update_layout(
            title='Attendance Trends (Last 30 Days)',
            xaxis_title='Date',
            yaxis_title='Students Present',
            hovermode='x'
        )
        
        # Calculate statistics
        if counts:
            avg_attendance = np.mean(counts)
            trend = np.polyfit(range(len(counts)), counts, 1)[0]
        else:
            avg_attendance = 0
            trend = 0
        
        return {
            'chart_json': json.loads(fig.to_json()),
            'average': float(avg_attendance),
            'trend_direction': 'increasing' if trend > 0 else 'decreasing',
            'trend_magnitude': float(trend)
        }
    
    def _generate_seating_heatmap(self, course_id: str, date: str) -> Dict:
        """
        Generate heatmap of where students sit
        Helps identify "back row" attendance issues
        """
        # Get seating data from camera analytics
        query = """
        SELECT seat_row, seat_col, COUNT(*) as frequency
        FROM seating_positions
        WHERE course_id = ? AND date = ?
        GROUP BY seat_row, seat_col
        """
        
        results = self.db.execute(query, (course_id, date)).fetchall()
        
        # Create matrix
        max_row = max([r['seat_row'] for r in results]) if results else 10
        max_col = max([r['seat_col'] for r in results]) if results else 8
        
        heatmap_data = np.zeros((max_row + 1, max_col + 1))
        
        for row in results:
            heatmap_data[row['seat_row'], row['seat_col']] = row['frequency']
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Frequency")
        ))
        
        fig.update_layout(
            title='Student Seating Heatmap',
            xaxis_title='Seat Column',
            yaxis_title='Seat Row',
            height=500
        )
        
        # Identify problem areas
        back_rows = heatmap_data[-3:, :]  # Last 3 rows
        back_row_attendance = np.mean(back_rows) if back_rows.size > 0 else 0
        front_row_attendance = np.mean(heatmap_data[:3, :]) if heatmap_data[:3, :].size > 0 else 0
        
        return {
            'chart_json': json.loads(fig.to_json()),
            'back_row_attendance': float(back_row_attendance),
            'front_row_attendance': float(front_row_attendance),
            'attendance_gap': float(front_row_attendance - back_row_attendance)
        }
    
    def _predict_attendance_trends(self, course_id: str) -> Dict:
        """
        Predict future attendance patterns
        """
        # Get historical data
        query = """
        SELECT date, COUNT(*) as count
        FROM attendance
        WHERE course_id = ?
        GROUP BY date
        ORDER BY date
        LIMIT 60
        """
        
        results = self.db.execute(query, (course_id,)).fetchall()
        
        if len(results) < 7:
            return {'message': 'Insufficient data for prediction'}
        
        dates = [r['date'] for r in results]
        counts = [r['count'] for r in results]
        
        # Simple linear regression for trend
        x = np.arange(len(counts))
        z = np.polyfit(x, counts, 1)
        trend_line = np.poly1d(z)
        
        # Predict next 7 days
        next_days = 7
        future_x = np.arange(len(counts), len(counts) + next_days)
        predictions = trend_line(future_x)
        
        # Calculate confidence intervals
        residuals = counts - trend_line(x)
        std_error = np.std(residuals)
        
        lower_bound = predictions - 1.96 * std_error
        upper_bound = predictions + 1.96 * std_error
        
        # Determine if intervention needed
        predicted_avg = np.mean(predictions)
        current_avg = np.mean(counts[-7:])  # Last 7 days
        
        intervention_needed = predicted_avg < current_avg * 0.9  # 10% drop
        
        return {
            'predictions': predictions.tolist(),
            'lower_bound': lower_bound.tolist(),
            'upper_bound': upper_bound.tolist(),
            'confidence_level': 0.95,
            'trend_direction': 'declining' if z[0] < 0 else 'improving',
            'intervention_needed': bool(intervention_needed),
            'message': 'Attendance predicted to decline - consider intervention' if intervention_needed else 'Attendance stable'
        }
    
    def _generate_alerts(self, course_id: str, attendance_data: List) -> List:
        """
        Generate real-time alerts for anomalies
        """
        alerts = []
        
        # Check for sudden drops
        if len(attendance_data) > 5:
            recent = attendance_data[-5:]
            previous = attendance_data[-10:-5]
            
            recent_avg = np.mean([r['present'] for r in recent])
            previous_avg = np.mean([r['present'] for r in previous])
            
            if recent_avg < previous_avg * 0.7:
                alerts.append({
                    'type': 'warning',
                    'message': f'⚠️ Attendance dropped by {(1 - recent_avg/previous_avg)*100:.1f}% recently',
                    'severity': 'high'
                })
        
        # Check for specific students at risk
        at_risk_students = self._identify_at_risk_students(course_id)
        if at_risk_students:
            alerts.append({
                'type': 'danger',
                'message': f'⚠️ {len(at_risk_students)} students at risk of failing attendance requirements',
                'students': at_risk_students,
                'severity': 'critical'
            })
        
        return alerts
    
    def _identify_at_risk_students(self, course_id: str) -> List:
        """
        Identify students with poor attendance
        """
        query = """
        SELECT student_name, 
               COUNT(*) as present_days,
               (SELECT COUNT(DISTINCT date) FROM classes WHERE course_id = ?) as total_days
        FROM attendance
        WHERE course_id = ?
        GROUP BY student_id
        HAVING (present_days * 1.0 / total_days) < 0.75
        """
        
        results = self.db.execute(query, (course_id, course_id)).fetchall()
        
        return [{'name': r['student_name'], 'percentage': r['present_days']/r['total_days']*100} 
                for r in results]