# backend/app/core/advanced_liveness.py
"""
Advanced anti-spoofing system that solves the proxy attendance problem
by ensuring only live humans are verified.
"""

import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model
import dlib
import logging
from typing import Dict, Tuple, List
import time

class AdvancedLivenessDetector:
    """
    Multi-modal liveness detection combining:
    1. Blink detection (active)
    2. Head movement (active)
    3. Texture analysis (passive - detects screens/prints)
    4. Optical flow (passive - detects natural motion)
    5. Heartbeat estimation (advanced - detects micro-movements)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize detectors
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
        
        # MediaPipe for face mesh (468 points)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Load pre-trained texture analysis model (detects prints/screens)
        self.texture_model = load_model('models/liveness_texture_model.h5')
        
        # Constants
        self.EYE_AR_THRESH = 0.25
        self.EYE_AR_CONSEC_FRAMES = 2
        self.HEAD_MOVEMENT_THRESH = 0.02
        
        # State tracking
        self.blink_counter = 0
        self.head_pose_history = []
        self.verification_score = 0.0
        
    def verify_liveness_advanced(self, frames: List[np.ndarray]) -> Dict:
        """
        Comprehensive liveness verification using multiple techniques
        """
        results = {
            'verified': False,
            'confidence': 0.0,
            'blinks_detected': 0,
            'texture_score': 0.0,
            'motion_score': 0.0,
            'heartbeat_score': 0.0,
            'message': ''
        }
        
        if len(frames) < 30:
            results['message'] = 'Insufficient frames for verification'
            return results
        
        # 1. Blink Detection (Active)
        blink_score = self._detect_blinks(frames)
        results['blinks_detected'] = blink_score['count']
        
        # 2. Texture Analysis (Passive - detects prints/screens)
        texture_score = self._analyze_texture(frames[-1])
        results['texture_score'] = texture_score
        
        # 3. Head Movement Analysis (Active)
        movement_score = self._analyze_head_movement(frames)
        results['motion_score'] = movement_score
        
        # 4. Heartbeat Estimation (Advanced - detects pulse micro-movements)
        heartbeat_score = self._estimate_heartbeat(frames)
        results['heartbeat_score'] = heartbeat_score
        
        # Weighted combination
        weights = {
            'blink': 0.35,      # Active verification
            'texture': 0.25,     # Passive anti-spoofing
            'movement': 0.25,    # Natural motion
            'heartbeat': 0.15     # Advanced liveness
        }
        
        total_confidence = (
            weights['blink'] * (min(blink_score['count'], 3) / 3) +
            weights['texture'] * texture_score +
            weights['movement'] * movement_score +
            weights['heartbeat'] * heartbeat_score
        )
        
        results['confidence'] = total_confidence
        results['verified'] = total_confidence > 0.75  # Threshold
        
        if results['verified']:
            results['message'] = f"✅ Liveness verified (Confidence: {total_confidence:.2%})"
        else:
            results['message'] = "❌ Liveness check failed - possible spoofing attempt"
            
        return results
    
    def _detect_blinks(self, frames: List[np.ndarray]) -> Dict:
        """
        Detect natural eye blinks over frame sequence
        """
        blink_count = 0
        ear_values = []
        
        for frame in frames[::3]:  # Sample every 3rd frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector(gray, 0)
            
            if len(faces) == 0:
                continue
                
            face = faces[0]
            landmarks = self.shape_predictor(gray, face)
            
            # Extract eye landmarks
            left_eye = []
            right_eye = []
            for i in range(36, 42):
                left_eye.append((landmarks.part(i).x, landmarks.part(i).y))
            for i in range(42, 48):
                right_eye.append((landmarks.part(i).x, landmarks.part(i).y))
            
            # Calculate Eye Aspect Ratio
            left_ear = self._eye_aspect_ratio(np.array(left_eye))
            right_ear = self._eye_aspect_ratio(np.array(right_eye))
            ear = (left_ear + right_ear) / 2.0
            ear_values.append(ear)
        
        # Detect blink patterns (EAR drops below threshold then rises)
        for i in range(1, len(ear_values)):
            if ear_values[i] < self.EYE_AR_THRESH and ear_values[i-1] > self.EYE_AR_THRESH:
                blink_count += 1
        
        return {
            'count': blink_count,
            'pattern_natural': 1 <= blink_count <= 5  # Natural range
        }
    
    def _analyze_texture(self, frame: np.ndarray) -> float:
        """
        Detect printed photos or screens via texture analysis
        """
        # Extract face ROI
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector(gray, 0)
        
        if len(faces) == 0:
            return 0.0
            
        face = faces[0]
        x, y, w, h = (face.left(), face.top(), face.width(), face.height())
        face_roi = frame[y:y+h, x:x+w]
        
        if face_roi.size == 0:
            return 0.0
            
        # Resize for model
        face_resized = cv2.resize(face_roi, (224, 224))
        face_normalized = face_resized / 255.0
        face_expanded = np.expand_dims(face_normalized, axis=0)
        
        # Predict liveness (1 = real, 0 = fake)
        prediction = self.texture_model.predict(face_expanded, verbose=0)
        
        # Additional frequency domain analysis (detects screen patterns)
        face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        fft = np.fft.fft2(face_gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = 20 * np.log(np.abs(fft_shift) + 1)
        
        # High frequency components indicate screen patterns
        high_freq_ratio = np.sum(magnitude > np.percentile(magnitude, 90)) / magnitude.size
        
        # Combine predictions
        texture_confidence = float(prediction[0][0])
        screen_penalty = 0.5 if high_freq_ratio > 0.15 else 1.0
        
        return texture_confidence * screen_penalty
    
    def _analyze_head_movement(self, frames: List[np.ndarray]) -> float:
        """
        Detect natural head movement patterns
        """
        movements = []
        
        for i in range(1, len(frames)):
            # Calculate optical flow between frames
            prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, curr_gray, None,
                0.5, 3, 15, 3, 5, 1.2, 0
            )
            
            # Calculate average movement magnitude
            mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            avg_movement = np.mean(mag)
            movements.append(avg_movement)
        
        if not movements:
            return 0.0
            
        # Natural movement has variability
        avg_movement = np.mean(movements)
        movement_std = np.std(movements)
        
        # Score based on natural movement patterns
        if 0.5 < avg_movement < 5.0 and movement_std > 0.5:
            return 0.9
        elif avg_movement < 0.1:  # Too still - possible photo
            return 0.2
        else:
            return 0.5
    
    def _estimate_heartbeat(self, frames: List[np.ndarray]) -> float:
        """
        Advanced: Estimate heartbeat from micro-movements
        (Detects subtle color changes in face due to blood flow)
        """
        # This is an advanced technique - simplified implementation
        face_regions = []
        
        for frame in frames[::2]:  # Sample every other frame
            # Convert to YUV color space for luminance analysis
            yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
            
            # Extract forehead region (where pulse is visible)
            h, w = frame.shape[:2]
            forehead = yuv[int(h*0.1):int(h*0.3), int(w*0.3):int(w*0.7)]
            
            if forehead.size > 0:
                avg_luminance = np.mean(forehead[:, :, 0])  # Y channel
                face_regions.append(avg_luminance)
        
        if len(face_regions) < 10:
            return 0.5
            
        # Analyze temporal variation (should have periodic pattern)
        variations = np.diff(face_regions)
        variation_std = np.std(variations)
        
        # Natural faces have small but consistent variations
        if 0.5 < variation_std < 5.0:
            return 0.8
        else:
            return 0.3
    
    def _eye_aspect_ratio(self, eye):
        """Calculate eye aspect ratio"""
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        return (A + B) / (2.0 * C)