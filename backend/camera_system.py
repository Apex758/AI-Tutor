import cv2
import threading
import numpy as np
import time
import os
from typing import Dict, Any, Optional

IMAGE_OUTPUT_DIR = "camera_captures"

class CameraSystem:
    
    def __init__(self, emotion_analyzer=None):
        self.camera = None
        self.is_running = False
        self.emotion_analyzer = emotion_analyzer
        self.frame_size = (640, 480)
        self.fps = 30
        self.processing_thread = None
        self.thread_stop_event = threading.Event()
        self.latest_frame = None
        
        os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
        
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.face_detection_enabled = True
        except Exception as e:
            print(f"Face detection not available: {e}")
            self.face_detection_enabled = False
    
    def start(self) -> bool:
        try:
            if self.camera is not None:
                return True
            
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                return False
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_size[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_size[1])
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            self.thread_stop_event.clear()
            self.processing_thread = threading.Thread(target=self._process_frames)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            self.is_running = True
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop(self) -> bool:
        try:
            if self.camera is None:
                return True
            
            self.thread_stop_event.set()
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=3.0)
            
            self.camera.release()
            self.camera = None
            self.is_running = False
            return True
        except Exception as e:
            print(f"Error stopping camera: {e}")
            return False
    
    def capture_image(self) -> Optional[Dict[str, Any]]:
        try:
            if self.camera is None:
                if not self.start():
                    return None
                time.sleep(0.5)
            
            ret, frame = self.camera.read()
            if not ret:
                return None
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
            filepath = os.path.join(IMAGE_OUTPUT_DIR, filename)
            cv2.imwrite(filepath, frame)
            
            analysis = self._analyze_frame(frame)
            
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "timestamp": timestamp,
                "analysis": analysis
            }
        except Exception as e:
            print(f"Error capturing image: {e}")
            return None
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        return self.latest_frame
    
    def _process_frames(self):
        last_emotion_time = 0
        emotion_interval = 1.0
        
        while not self.thread_stop_event.is_set():
            try:
                if self.camera is None:
                    time.sleep(0.1)
                    continue
                
                ret, frame =