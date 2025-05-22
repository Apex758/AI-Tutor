"""
Emotion Analyzer
"""

import cv2
import numpy as np
import dlib
from typing import Dict, Optional
from datetime import datetime

class EmotionAnalyzer:
    
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        
        try:
            predictor_path = "shape_predictor_68_face_landmarks.dat"
            self.predictor = dlib.shape_predictor(predictor_path)
            self.landmarks_available = True
        except:
            self.landmarks_available = False
            print("Facial landmarks predictor not available - using basic emotion detection")
        
        self.emotion_thresholds = {
            'stress': 0.7,
            'neutral': 0.3,
            'relaxed': 0.4
        }
        
        self.current_emotion_data = None
    
    def analyze_frame(self, frame: np.ndarray) -> Optional[Dict]:
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)
            
            if not faces:
                return self._get_empty_result()
            
            face = faces[0]
            
            if self.landmarks_available:
                landmarks = self.predictor(gray, face)
                features = self._extract_features(landmarks)
                emotion_data = self._analyze_emotions(features)
            else:
                emotion_data = self._basic_emotion_analysis(face, gray)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'face_detected': True,
                'emotions': emotion_data,
                'metrics': {
                    'movement': 0.2,
                    'blink_rate': 15.0,
                    'facial_tension': emotion_data.get('stress_level', 0.3)
                }
            }
            
            self.current_emotion_data = result
            return result
            
        except Exception as e:
            print(f"Error in emotion analysis: {e}")
            return self._get_empty_result()
    
    def get_current_emotion(self) -> Optional[Dict]:
        return self.current_emotion_data
    
    def _extract_features(self, landmarks) -> Dict:
        features = {
            'eye_aspect_ratio': self._calculate_eye_aspect_ratio(landmarks),
            'mouth_aspect_ratio': self._calculate_mouth_aspect_ratio(landmarks),
            'eyebrow_position': self._calculate_eyebrow_position(landmarks),
            'facial_symmetry': 0.8  # Simplified
        }
        return features
    
    def _analyze_emotions(self, features: Dict) -> Dict:
        stress_indicators = [
            features['eye_aspect_ratio'] < 0.2,
            features['eyebrow_position'] > 0.6,
            features['facial_symmetry'] < 0.8
        ]
        
        stress_score = sum(stress_indicators) / len(stress_indicators)
        
        if stress_score > self.emotion_thresholds['stress']:
            primary_emotion = 'stressed'
        elif stress_score < self.emotion_thresholds['neutral']:
            primary_emotion = 'relaxed'
        else:
            primary_emotion = 'neutral'
        
        return {
            'primary': primary_emotion,
            'confidence': 0.8,
            'stress_level': stress_score,
            'intensity': 0.5
        }
    
    def _basic_emotion_analysis(self, face, gray) -> Dict:
        # Basic emotion detection without landmarks
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        face_roi = gray[y:y+h, x:x+w]
        
        # Simple heuristics based on face region intensity
        avg_intensity = np.mean(face_roi)
        
        if avg_intensity < 100:
            primary_emotion = 'stressed'
            stress_level = 0.7
        elif avg_intensity > 150:
            primary_emotion = 'relaxed'
            stress_level = 0.2
        else:
            primary_emotion = 'neutral'
            stress_level = 0.4
        
        return {
            'primary': primary_emotion,
            'confidence': 0.6,
            'stress_level': stress_level,
            'intensity': 0.5
        }
    
    def _calculate_eye_aspect_ratio(self, landmarks) -> float:
        try:
            left_eye = [(landmarks.part(36+i).x, landmarks.part(36+i).y) for i in range(6)]
            right_eye = [(landmarks.part(42+i).x, landmarks.part(42+i).y) for i in range(6)]
            
            left_ear = self._eye_aspect_ratio(left_eye)
            right_ear = self._eye_aspect_ratio(right_eye)
            
            return (left_ear + right_ear) / 2
        except:
            return 0.3  # Default value
    
    def _eye_aspect_ratio(self, eye_points) -> float:
        try:
            v1 = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
            v2 = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
            h = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
            
            return (v1 + v2) / (2.0 * h) if h > 0 else 0
        except:
            return 0.3
    
    def _calculate_mouth_aspect_ratio(self, landmarks) -> float:
        try:
            mouth_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(48, 68)]
            v = np.linalg.norm(np.array(mouth_points[2]) - np.array(mouth_points[10]))
            h = np.linalg.norm(np.array(mouth_points[0]) - np.array(mouth_points[6]))
            return v / h if h > 0 else 0
        except:
            return 0.4
    
    def _calculate_eyebrow_position(self, landmarks) -> float:
        try:
            eyebrow_points = [landmarks.part(i).y for i in range(17, 27)]
            eye_points = [landmarks.part(i).y for i in range(36, 48)]
            
            avg_eyebrow = sum(eyebrow_points) / len(eyebrow_points)
            avg_eye = sum(eye_points) / len(eye_points)
            
            return (avg_eye - avg_eyebrow) / 100
        except:
            return 0.3
    
    def _get_empty_result(self) -> Dict:
        return {
            'timestamp': datetime.now().isoformat(),
            'face_detected': False,
            'emotions': {
                'primary': 'unknown',
                'confidence': 0.0,
                'stress_level': 0.0,
                'intensity': 0.0
            },
            'metrics': {
                'movement': 0.0,
                'blink_rate': 0.0,
                'facial_tension': 0.0
            }
        }