"""
Camera Commands Module
"""

from typing import Dict, Any

class CameraCommands:
    
    def __init__(self, camera_system=None):
        self.camera_system = camera_system
    
    def execute(self, command_type: str, text: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        
        if command_type == "camera_on":
            return self._start_camera()
        elif command_type == "camera_off":
            return self._stop_camera()
        elif command_type == "take_photo":
            return self._capture_photo()
        else:
            return {
                "success": False,
                "response": f"Unknown camera command: {command_type}",
                "scene": [],
                "final_answer": {}
            }
    
    def _start_camera(self) -> Dict[str, Any]:
        if not self.camera_system:
            return {
                "success": False,
                "response": "Camera system not available",
                "scene": [],
                "final_answer": {}
            }
        
        success = self.camera_system.start()
        return {
            "success": success,
            "response": "Camera started successfully" if success else "Failed to start camera",
            "scene": [],
            "final_answer": {}
        }
    
    def _stop_camera(self) -> Dict[str, Any]:
        if not self.camera_system:
            return {
                "success": False,
                "response": "Camera system not available",
                "scene": [],
                "final_answer": {}
            }
        
        success = self.camera_system.stop()
        return {
            "success": success,
            "response": "Camera stopped successfully" if success else "Failed to stop camera",
            "scene": [],
            "final_answer": {}
        }
    
    def _capture_photo(self) -> Dict[str, Any]:
        if not self.camera_system:
            return {
                "success": False,
                "response": "Camera system not available",
                "scene": [],
                "final_answer": {}
            }
        
        if not self.camera_system.is_running:
            self.camera_system.start()
        
        result = self.camera_system.capture_image()
        
        if result:
            return {
                "success": True,
                "response": f"Photo captured successfully: {result.get('filename', 'image.jpg')}",
                "scene": [],
                "final_answer": {}
            }
        else:
            return {
                "success": False,
                "response": "Failed to capture photo",
                "scene": [],
                "final_answer": {}
            }
    
    def get_available_commands(self) -> list:
        return ["camera_on", "camera_off", "take_photo"]