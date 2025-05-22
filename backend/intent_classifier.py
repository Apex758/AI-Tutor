"""
Intent Classifier - Determines user intent and extracts topics
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class IntentPattern:
    pattern: str
    intent: str
    confidence: float
    keywords: List[str]

class IntentClassifier:
    """
    Classifies user intent to determine if input should be handled as:
    - Command (direct action)
    - Educational query (send to AI)
    """
    
    def __init__(self):
        self.command_patterns = [
            # Camera commands
            IntentPattern(
                pattern=r"(turn on|start|open|activate|enable).*(camera|cam)",
                intent="command",
                confidence=0.9,
                keywords=["camera", "turn on", "start", "activate"]
            ),
            IntentPattern(
                pattern=r"(turn off|stop|close|deactivate|disable).*(camera|cam)",
                intent="command",
                confidence=0.9,
                keywords=["camera", "turn off", "stop", "deactivate"]
            ),
            IntentPattern(
                pattern=r"(take|capture).*(photo|picture|image|snapshot)",
                intent="command",
                confidence=0.8,
                keywords=["take", "capture", "photo", "picture"]
            ),
            
            # Math operation commands
            IntentPattern(
                pattern=r"(add|plus|\+).*(\d+).*(\d+)",
                intent="command",
                confidence=0.8,
                keywords=["add", "plus", "numbers"]
            ),
            IntentPattern(
                pattern=r"(subtract|minus|\-).*(\d+).*(\d+)",
                intent="command",
                confidence=0.8,
                keywords=["subtract", "minus", "numbers"]
            ),
            IntentPattern(
                pattern=r"(multiply|times|\*).*(\d+).*(\d+)",
                intent="command",
                confidence=0.8,
                keywords=["multiply", "times", "numbers"]
            ),
            IntentPattern(
                pattern=r"(divide|divided by|\/).*(\d+).*(\d+)",
                intent="command",
                confidence=0.8,
                keywords=["divide", "numbers"]
            ),
            
            # Clear/reset commands
            IntentPattern(
                pattern=r"(clear|clean|erase|reset).*(board|screen|canvas)",
                intent="command",
                confidence=0.9,
                keywords=["clear", "clean", "board", "screen"]
            ),
            
            # Drawing commands
            IntentPattern(
                pattern=r"(draw|show me|display).*(apple|apples)",
                intent="command",
                confidence=0.7,
                keywords=["draw", "show", "apple"]
            ),
            IntentPattern(
                pattern=r"(draw|show me|display).*(circle|circles)",
                intent="command",
                confidence=0.7,
                keywords=["draw", "show", "circle"]
            ),
            
            # Timer commands
            IntentPattern(
                pattern=r"(set|start).*(timer|alarm).*(\d+).*(minute|second)",
                intent="command",
                confidence=0.8,
                keywords=["timer", "set", "minute", "second"]
            ),
            
            # Weather commands
            IntentPattern(
                pattern=r"(weather|temperature).*in.*([A-Za-z\s]+)",
                intent="command",
                confidence=0.7,
                keywords=["weather", "temperature"]
            )
        ]
        
        # Educational patterns indicate queries that should go to AI
        self.educational_patterns = [
            IntentPattern(
                pattern=r"(explain|teach|how|why|what|when|where)",
                intent="educational",
                confidence=0.6,
                keywords=["explain", "teach", "how", "why", "what"]
            ),
            IntentPattern(
                pattern=r"(help me|can you|could you|show me how)",
                intent="educational",
                confidence=0.7,
                keywords=["help", "show me", "how"]
            ),
            IntentPattern(
                pattern=r"(i don't understand|confused|help)",
                intent="educational", 
                confidence=0.8,
                keywords=["understand", "confused", "help"]
            ),
            IntentPattern(
                pattern=r"(solve|work out|figure out|calculate)",
                intent="educational",
                confidence=0.6,
                keywords=["solve", "work out", "calculate"]
            )
        ]
        
        # Topic extraction patterns
        self.topic_patterns = {
            "math": [
                r"(math|mathematics|arithmetic|algebra|geometry)",
                r"(add|subtract|multiply|divide|plus|minus|times)",
                r"(equation|problem|calculate|solve|number)",
                r"(fraction|decimal|percent|ratio)"
            ],
            "science": [
                r"(science|physics|chemistry|biology)",
                r"(experiment|hypothesis|theory|law)",
                r"(atom|molecule|element|compound)",
                r"(gravity|force|energy|motion)"
            ],
            "reading": [
                r"(reading|literature|story|book|poem)",
                r"(character|plot|theme|setting)",
                r"(comprehension|vocabulary|spelling)"
            ],
            "writing": [
                r"(writing|essay|paragraph|sentence)",
                r"(grammar|punctuation|spelling)",
                r"(creative writing|story|report)"
            ],
            "history": [
                r"(history|historical|ancient|medieval|modern)",
                r"(war|battle|revolution|empire|civilization)",
                r"(president|king|queen|leader|government)"
            ],
            "geography": [
                r"(geography|country|continent|city|state)",
                r"(mountain|river|ocean|desert|forest)",
                r"(capital|population|climate|weather)"
            ]
        }
        
        print("Intent Classifier initialized")
    
    def classify_intent(self, text: str) -> Dict[str, Any]:
        """
        Classify user intent as command or educational query
        
        Returns:
            Dictionary with intent type, confidence, and extracted information
        """
        text_lower = text.lower().strip()
        
        # Check for command patterns first (higher priority)
        command_result = self._check_patterns(text_lower, self.command_patterns)
        if command_result["confidence"] > 0.6:
            return {
                "intent": "command",
                "confidence": command_result["confidence"],
                "matched_pattern": command_result["pattern"],
                "keywords": command_result["keywords"],
                "original_text": text
            }
        
        # Check for educational patterns
        educational_result = self._check_patterns(text_lower, self.educational_patterns)
        if educational_result["confidence"] > 0.5:
            return {
                "intent": "educational",
                "confidence": educational_result["confidence"],
                "matched_pattern": educational_result["pattern"],
                "keywords": educational_result["keywords"],
                "original_text": text
            }
        
        # Default to educational if no clear command pattern
        # Most student inputs will be questions or requests for help
        return {
            "intent": "educational",
            "confidence": 0.5,
            "matched_pattern": None,
            "keywords": [],
            "original_text": text
        }
    
    def extract_topic(self, text: str) -> Optional[str]:
        """
        Extract the main educational topic from the text
        
        Returns:
            Topic name or None if no clear topic is identified
        """
        text_lower = text.lower()
        
        # Check each topic pattern
        for topic, patterns in self.topic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return topic
        
        # Try to extract topic from common question patterns
        topic_indicators = [
            r"learn about (.+)",
            r"help with (.+)",
            r"explain (.+)",
            r"teach me (.+)",
            r"study (.+)",
            r"understand (.+)"
        ]
        
        for pattern in topic_indicators:
            match = re.search(pattern, text_lower)
            if match:
                extracted = match.group(1).strip()
                # Clean up the extracted topic
                extracted = re.sub(r"[^a-zA-Z\s]", "", extracted)
                if len(extracted) > 2 and len(extracted) < 50:
                    return extracted
        
        return None
    
    def extract_numbers(self, text: str) -> List[float]:
        """
        Extract numbers from text for math operations
        """
        # Pattern to match integers and decimals
        number_pattern = r'-?\d+\.?\d*'
        matches = re.findall(number_pattern, text)
        
        numbers = []
        for match in matches:
            try:
                # Convert to float first, then to int if it's a whole number
                num = float(match)
                if num.is_integer():
                    numbers.append(int(num))
                else:
                    numbers.append(num)
            except ValueError:
                continue
        
        return numbers
    
    def extract_grade_level(self, text: str) -> Optional[str]:
        """
        Extract grade level from text
        """
        grade_patterns = [
            r"grade\s*([1-6]|one|two|three|four|five|six)",
            r"([1-6])(st|nd|rd|th)\s*grade",
            r"kindergarten|k-?\d",
            r"elementary|primary",
            r"first|second|third|fourth|fifth|sixth"
        ]
        
        text_lower = text.lower()
        
        for pattern in grade_patterns:
            match = re.search(pattern, text_lower)
            if match:
                grade_text = match.group(0)
                
                # Normalize grade level
                if "kindergarten" in grade_text or "k" in grade_text:
                    return "kindergarten"
                elif "1" in grade_text or "first" in grade_text:
                    return "first_grade"
                elif "2" in grade_text or "second" in grade_text:
                    return "second_grade"
                elif "3" in grade_text or "third" in grade_text:
                    return "third_grade"
                elif "4" in grade_text or "fourth" in grade_text:
                    return "fourth_grade"
                elif "5" in grade_text or "fifth" in grade_text:
                    return "fifth_grade"
                elif "6" in grade_text or "sixth" in grade_text:
                    return "sixth_grade"
                elif "elementary" in grade_text or "primary" in grade_text:
                    return "elementary"
        
        return None
    
    def _check_patterns(self, text: str, patterns: List[IntentPattern]) -> Dict[str, Any]:
        """
        Check text against a list of patterns and return best match
        """
        best_match = {
            "confidence": 0.0,
            "pattern": None,
            "keywords": []
        }
        
        for pattern_obj in patterns:
            # Check regex pattern
            regex_match = re.search(pattern_obj.pattern, text)
            confidence = 0.0
            
            if regex_match:
                confidence = pattern_obj.confidence
            else:
                # Check for keyword matches
                keyword_matches = sum(1 for keyword in pattern_obj.keywords if keyword in text)
                if keyword_matches > 0:
                    confidence = (keyword_matches / len(pattern_obj.keywords)) * 0.5
            
            if confidence > best_match["confidence"]:
                best_match.update({
                    "confidence": confidence,
                    "pattern": pattern_obj.pattern,
                    "keywords": pattern_obj.keywords
                })
        
        return best_match
    
    def get_command_type(self, text: str) -> Optional[str]:
        """
        Determine specific command type for command intents
        """
        text_lower = text.lower()
        
        # Camera commands
        if any(word in text_lower for word in ["camera", "cam"]):
            if any(word in text_lower for word in ["on", "start", "open", "activate"]):
                return "camera_on"
            elif any(word in text_lower for word in ["off", "stop", "close", "deactivate"]):
                return "camera_off"
            elif any(word in text_lower for word in ["take", "capture", "photo", "picture"]):
                return "take_photo"
        
        # Math commands
        if any(word in text_lower for word in ["add", "plus", "+"]):
            return "math_addition"
        elif any(word in text_lower for word in ["subtract", "minus", "-"]):
            return "math_subtraction"
        elif any(word in text_lower for word in ["multiply", "times", "*"]):
            return "math_multiplication"
        elif any(word in text_lower for word in ["divide", "/"]):
            return "math_division"
        
        # Drawing commands
        if "draw" in text_lower or "show" in text_lower:
            if "apple" in text_lower:
                return "draw_apple"
            elif "circle" in text_lower:
                return "draw_circle"
        
        # Clear commands
        if any(word in text_lower for word in ["clear", "clean", "erase", "reset"]):
            return "clear_board"
        
        # Timer commands
        if "timer" in text_lower:
            return "set_timer"
        
        # Weather commands
        if "weather" in text_lower or "temperature" in text_lower:
            return "get_weather"
        
        return None