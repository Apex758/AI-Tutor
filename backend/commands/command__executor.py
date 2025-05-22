"""
Command Executor - Main orchestrator for all commands
Delegates to specific command modules based on command type
"""

from typing import Dict, Any, Optional
from backend.commands.math_commands import MathCommands
from backend.commands.camera_commands import CameraCommands
from backend.commands.learning_commands import LearningCommands
from backend.commands.general_commands import GeneralCommands

class CommandExecutor:
    """
    Main command executor that delegates to specific command modules
    """
    
    def __init__(self, camera_system=None, learning_tracker=None):
        self.camera_system = camera_system
        self.learning_tracker = learning_tracker
        
        # Initialize command modules
        self.math_commands = MathCommands(learning_tracker=learning_tracker)
        self.camera_commands = CameraCommands(camera_system=camera_system)
        self.learning_commands = LearningCommands(learning_tracker=learning_tracker)
        self.general_commands = GeneralCommands()
        
        print("Command Executor initialized with all command modules")
    
    def execute_command(self, text: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command based on the intent classification result
        
        Args:
            text: Original text input
            intent_result: Result from intent classifier
            
        Returns:
            Command execution result
        """
        try:
            # Extract command type from intent classifier
            from backend.intent_classifier import IntentClassifier
            classifier = IntentClassifier()
            command_type = classifier.get_command_type(text)
            
            if not command_type:
                return {
                    "success": False,
                    "response": "Could not determine command type",
                    "scene": [],
                    "final_answer": {}
                }
            
            print(f"Executing command: {command_type}")
            
            # Delegate to appropriate command module
            if command_type.startswith("math_"):
                return self.math_commands.execute(command_type, text, intent_result)
            
            elif command_type.startswith("camera_") or command_type == "take_photo":
                return self.camera_commands.execute(command_type, text, intent_result)
            
            elif command_type.startswith("learning_") or command_type == "assess_knowledge":
                return self.learning_commands.execute(command_type, text, intent_result)
            
            elif command_type.startswith("draw_") or command_type == "clear_board":
                return self.general_commands.execute(command_type, text, intent_result)
            
            elif command_type in ["get_weather", "set_timer", "search_info"]:
                return self.general_commands.execute(command_type, text, intent_result)
            
            else:
                # Try to execute with general commands as fallback
                return self.general_commands.execute(command_type, text, intent_result)
                
        except Exception as e:
            print(f"Error executing command: {e}")
            return {
                "success": False,
                "response": f"Error executing command: {str(e)}",
                "scene": [],
                "final_answer": {}
            }
    
    def get_available_commands(self) -> Dict[str, List[str]]:
        """
        Get list of all available commands organized by category
        """
        return {
            "math": self.math_commands.get_available_commands(),
            "camera": self.camera_commands.get_available_commands(),
            "learning": self.learning_commands.get_available_commands(),
            "general": self.general_commands.get_available_commands()
        }