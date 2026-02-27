# backend/app/core/offline_sync.py
"""
Offline-first architecture ensuring system works without internet
"""

import sqlite3
import json
import hashlib
from datetime import datetime
import threading
import time
import requests

class OfflineSyncManager:
    """
    Manages offline data synchronization
    Ensures system works 100% offline and syncs when connected
    """
    
    def __init__(self, local_db_path='data/local_attendance.db', sync_url=None):
        self.local_db_path = local_db_path
        self.sync_url = sync_url
        self.sync_queue = []
        self.is_online = False
        self.init_local_db()
        
        # Start sync thread
        self.sync_thread = threading.Thread(target=self._sync_worker)
        self.sync_thread.daemon = True
        self.sync_thread.start()
    
    def init_local_db(self):
        """Initialize local SQLite database for offline storage"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS offline_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            student_name TEXT,
            course_id TEXT,
            timestamp TEXT,
            confidence REAL,
            image_hash TEXT,
            synced INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT,
            data_json TEXT,
            attempts INTEGER DEFAULT 0,
            last_attempt TEXT,
            synced INTEGER DEFAULT 0
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_encodings_local (
            student_id TEXT PRIMARY KEY,
            student_name TEXT,
            encoding_json TEXT,
            updated_at TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def mark_attendance_offline(self, student_id, student_name, course_id, confidence, face_image=None):
        """
        Mark attendance while offline - stores locally
        """
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        # Generate image hash for integrity
        image_hash = None
        if face_image is not None:
            image_hash = hashlib.sha256(face_image).hexdigest()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO offline_attendance 
        (student_id, student_name, course_id, timestamp, confidence, image_hash)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_id, student_name, course_id, timestamp, confidence, image_hash))
        
        attendance_id = cursor.lastrowid
        
        # Add to sync queue
        sync_data = {
            'attendance_id': attendance_id,
            'student_id': student_id,
            'student_name': student_name,
            'course_id': course_id,
            'timestamp': timestamp,
            'confidence': confidence,
            'image_hash': image_hash
        }
        
        cursor.execute('''
        INSERT INTO sync_queue (data_type, data_json, attempts)
        VALUES (?, ?, ?)
        ''', ('attendance', json.dumps(sync_data), 0))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'offline_id': attendance_id,
            'message': 'Attendance recorded offline - will sync when online'
        }
    
    def _sync_worker(self):
        """
        Background thread that attempts to sync when online
        """
        while True:
            try:
                # Check connectivity
                self.is_online = self._check_connectivity()
                
                if self.is_online:
                    self._sync_pending_data()
                
                time.sleep(60)  # Check every minute
            except:
                time.sleep(120)  # Back off on error
    
    def _check_connectivity(self):
        """Check if backend is reachable"""
        if not self.sync_url:
            return False
        
        try:
            response = requests.get(f"{self.sync_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _sync_pending_data(self):
        """Sync all pending data to cloud"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        # Get unsynced items
        cursor.execute('''
        SELECT * FROM sync_queue 
        WHERE synced = 0 AND attempts < 5
        ORDER BY id ASC
        ''')
        
        pending = cursor.fetchall()
        
        for item in pending:
            try:
                data = json.loads(item[2])  # data_json
                
                # Attempt to sync
                response = requests.post(
                    f"{self.sync_url}/api/sync/attendance",
                    json=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    # Mark as synced
                    cursor.execute('''
                    UPDATE sync_queue 
                    SET synced = 1 
                    WHERE id = ?
                    ''', (item[0],))
                    
                    # Update attendance record
                    cursor.execute('''
                    UPDATE offline_attendance 
                    SET synced = 1 
                    WHERE id = ?
                    ''', (data['attendance_id'],))
                    
                    conn.commit()
                else:
                    # Increment attempt count
                    cursor.execute('''
                    UPDATE sync_queue 
                    SET attempts = attempts + 1,
                        last_attempt = ?
                    WHERE id = ?
                    ''', (datetime.now().isoformat(), item[0]))
                    
                    conn.commit()
            
            except Exception as e:
                print(f"Sync error: {e}")
        
        conn.close()
    
    def get_offline_stats(self):
        """Get statistics about offline records"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN synced = 1 THEN 1 ELSE 0 END) as synced,
            SUM(CASE WHEN synced = 0 THEN 1 ELSE 0 END) as pending
        FROM offline_attendance
        ''')
        
        stats = cursor.fetchone()
        
        cursor.execute('SELECT COUNT(*) FROM sync_queue WHERE synced = 0')
        queue_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_records': stats[0] if stats else 0,
            'synced': stats[1] if stats else 0,
            'pending_sync': stats[2] if stats else 0,
            'queue_size': queue_count,
            'online': self.is_online
        }