# backend/app/notifications/parent_alerts.py
"""
Automated parent notifications for attendance
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from twilio.rest import Client
import logging

class ParentNotificationSystem:
    """
    Sends real-time attendance alerts to parents
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Email config
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_sender = "attendance@embu.ac.ke"
        
        # SMS config (Twilio)
        self.twilio_client = None
        self.twilio_phone = None
        
        # Telegram config
        self.telegram_bot_token = None
        
    def configure_sms(self, account_sid, auth_token, from_phone):
        """Configure Twilio SMS"""
        self.twilio_client = Client(account_sid, auth_token)
        self.twilio_phone = from_phone
    
    def configure_telegram(self, bot_token):
        """Configure Telegram bot"""
        self.telegram_bot_token = bot_token
    
    def send_attendance_alert(self, student_name, parent_email, parent_phone, 
                              status, time, course):
        """
        Send multi-channel attendance alert
        """
        results = {'email': False, 'sms': False, 'telegram': False}
        
        # Email alert
        if parent_email:
            results['email'] = self._send_email(
                parent_email,
                student_name,
                status,
                time,
                course
            )
        
        # SMS alert
        if parent_phone and self.twilio_client:
            results['sms'] = self._send_sms(
                parent_phone,
                student_name,
                status,
                time,
                course
            )
        
        return results
    
    def _send_email(self, to_email, student_name, status, time, course):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = to_email
            msg['Subject'] = f"Attendance Alert: {student_name}"
            
            if status == 'present':
                body = f"""
                <html>
                <body>
                    <h2 style="color: #48bb78;">✅ Attendance Confirmed</h2>
                    <p>Dear Parent,</p>
                    <p>This is to confirm that <strong>{student_name}</strong> has been marked 
                    <strong style="color: #48bb78;">PRESENT</strong> for:</p>
                    <ul>
                        <li><strong>Course:</strong> {course}</li>
                        <li><strong>Time:</strong> {time}</li>
                        <li><strong>Method:</strong> Face Recognition + Liveness Check</li>
                    </ul>
                    <p>Thank you,<br>University of Embu Attendance System</p>
                </body>
                </html>
                """
            else:
                body = f"""
                <html>
                <body>
                    <h2 style="color: #f56565;">⚠️ Absence Alert</h2>
                    <p>Dear Parent,</p>
                    <p>This is to notify you that <strong>{student_name}</strong> has been marked 
                    <strong style="color: #f56565;">ABSENT</strong> for:</p>
                    <ul>
                        <li><strong>Course:</strong> {course}</li>
                        <li><strong>Time:</strong> {time}</li>
                    </ul>
                    <p>Please contact the university for more information.</p>
                    <p>Thank you,<br>University of Embu Attendance System</p>
                </body>
                </html>
                """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            # server.login(self.email_sender, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Email error: {e}")
            return False
    
    def _send_sms(self, to_phone, student_name, status, time, course):
        """Send SMS notification"""
        try:
            if status == 'present':
                message = f"✅ {student_name} marked PRESENT for {course} at {time}"
            else:
                message = f"⚠️ {student_name} marked ABSENT for {course} at {time}"
            
            self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=to_phone
            )
            return True
            
        except Exception as e:
            self.logger.error(f"SMS error: {e}")
            return False