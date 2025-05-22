"""
Math Commands Module - Handles all math-related commands
"""

import re
from typing import Dict, Any, List, Union, Optional

class MathCommands:
    """
    Handles all math operation commands with grade-appropriate explanations
    """
    
    def __init__(self, learning_tracker=None):
        self.learning_tracker = learning_tracker
        
        # Grade level teaching approaches
        self.grade_approaches = {
            "kindergarten": {
                "max_numbers": 10,
                "use_objects": True,
                "simple_language": True,
                "visual_heavy": True
            },
            "first_grade": {
                "max_numbers": 20,
                "use_objects": True,
                "simple_language": True,
                "visual_heavy": True
            },
            "second_grade": {
                "max_numbers": 100,
                "use_objects": False,
                "simple_language": True,
                "visual_heavy": True
            },
            "third_grade": {
                "max_numbers": 1000,
                "use_objects": False,
                "simple_language": False,
                "visual_heavy": False
            },
            "fourth_grade": {
                "max_numbers": 10000,
                "use_objects": False,
                "simple_language": False,
                "visual_heavy": False
            },
            "fifth_grade": {
                "max_numbers": 100000,
                "use_objects": False,
                "simple_language": False,
                "visual_heavy": False
            },
            "sixth_grade": {
                "max_numbers": 1000000,
                "use_objects": False,
                "simple_language": False,
                "visual_heavy": False
            }
        }
        
        print("Math Commands module initialized")
    
    def execute(self, command_type: str, text: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a math command
        """
        try:
            # Extract numbers from text
            numbers = self._extract_numbers(text)
            
            # Determine grade level
            grade_level = self._determine_grade_level(text, numbers)
            
            # Execute specific math operation
            if command_type == "math_addition":
                return self._handle_addition(numbers, grade_level, text)
            elif command_type == "math_subtraction":
                return self._handle_subtraction(numbers, grade_level, text)
            elif command_type == "math_multiplication":
                return self._handle_multiplication(numbers, grade_level, text)
            elif command_type == "math_division":
                return self._handle_division(numbers, grade_level, text)
            else:
                return {
                    "success": False,
                    "response": f"Unknown math command: {command_type}",
                    "scene": [],
                    "final_answer": {}
                }
                
        except Exception as e:
            print(f"Error in math command execution: {e}")
            return {
                "success": False,
                "response": f"Error in math calculation: {str(e)}",
                "scene": [],
                "final_answer": {}
            }
    
    def _handle_addition(self, numbers: List[Union[int, float]], grade_level: str, text: str) -> Dict[str, Any]:
        """
        Handle addition operations with grade-appropriate explanations
        """
        if len(numbers) < 2:
            return {
                "success": False,
                "response": "I need at least two numbers to add together.",
                "scene": [],
                "final_answer": {}
            }
        
        # Calculate result
        result = sum(numbers)
        
        # Get grade approach
        approach = self.grade_approaches.get(grade_level, self.grade_approaches["third_grade"])
        
        # Create explanation
        explanation = self._create_addition_explanation(numbers, result, approach, grade_level)
        
        # Create visual scene
        scene = self._create_addition_scene(numbers, result, approach)
        
        # Create final answer structure
        final_answer = {
            "correct_value": str(int(result) if result == int(result) else result),
            "explanation": f"Adding {' + '.join(str(n) for n in numbers)} equals {result}",
            "feedback_correct": "Excellent! You got the addition correct!",
            "feedback_incorrect": f"Not quite. When we add {' + '.join(str(n) for n in numbers)}, we get {result}."
        }
        
        # Log learning progress
        if self.learning_tracker:
            self.learning_tracker.mark_topic_encountered("math")
            self.learning_tracker.log_interaction("math_addition", text, f"Solved: {' + '.join(str(n) for n in numbers)} = {result}")
        
        return {
            "success": True,
            "response": explanation,
            "scene": scene,
            "final_answer": final_answer
        }
    
    def _handle_subtraction(self, numbers: List[Union[int, float]], grade_level: str, text: str) -> Dict[str, Any]:
        """
        Handle subtraction operations
        """
        if len(numbers) < 2:
            return {
                "success": False,
                "response": "I need at least two numbers for subtraction.",
                "scene": [],
                "final_answer": {}
            }
        
        # Calculate result (first number minus all others)
        result = numbers[0]
        for num in numbers[1:]:
            result -= num
        
        approach = self.grade_approaches.get(grade_level, self.grade_approaches["third_grade"])
        explanation = self._create_subtraction_explanation(numbers, result, approach, grade_level)
        scene = self._create_subtraction_scene(numbers, result, approach)
        
        final_answer = {
            "correct_value": str(int(result) if result == int(result) else result),
            "explanation": f"Subtracting gives us {result}",
            "feedback_correct": "Great job with subtraction!",
            "feedback_incorrect": f"The correct answer is {result}."
        }
        
        if self.learning_tracker:
            self.learning_tracker.mark_topic_encountered("math")
            self.learning_tracker.log_interaction("math_subtraction", text, f"Solved: {numbers[0]} - {' - '.join(str(n) for n in numbers[1:])} = {result}")
        
        return {
            "success": True,
            "response": explanation,
            "scene": scene,
            "final_answer": final_answer
        }
    
    def _handle_multiplication(self, numbers: List[Union[int, float]], grade_level: str, text: str) -> Dict[str, Any]:
        """
        Handle multiplication operations
        """
        if len(numbers) < 2:
            return {
                "success": False,
                "response": "I need at least two numbers to multiply.",
                "scene": [],
                "final_answer": {}
            }
        
        # Calculate result
        result = 1
        for num in numbers:
            result *= num
        
        approach = self.grade_approaches.get(grade_level, self.grade_approaches["third_grade"])
        explanation = self._create_multiplication_explanation(numbers, result, approach, grade_level)
        scene = self._create_multiplication_scene(numbers, result, approach)
        
        final_answer = {
            "correct_value": str(int(result) if result == int(result) else result),
            "explanation": f"Multiplying gives us {result}",
            "feedback_correct": "Perfect multiplication!",
            "feedback_incorrect": f"The correct answer is {result}."
        }
        
        if self.learning_tracker:
            self.learning_tracker.mark_topic_encountered("math")
            self.learning_tracker.log_interaction("math_multiplication", text, f"Solved: {' × '.join(str(n) for n in numbers)} = {result}")
        
        return {
            "success": True,
            "response": explanation,
            "scene": scene,
            "final_answer": final_answer
        }
    
    def _handle_division(self, numbers: List[Union[int, float]], grade_level: str, text: str) -> Dict[str, Any]:
        """
        Handle division operations
        """
        if len(numbers) < 2:
            return {
                "success": False,
                "response": "I need at least two numbers for division.",
                "scene": [],
                "final_answer": {}
            }
        
        # Check for division by zero
        if any(n == 0 for n in numbers[1:]):
            return {
                "success": False,
                "response": "I can't divide by zero. That's undefined in mathematics.",
                "scene": [],
                "final_answer": {}
            }
        
        # Calculate result
        result = numbers[0]
        for num in numbers[1:]:
            result /= num
        
        # Round to reasonable precision
        if result == int(result):
            result = int(result)
        else:
            result = round(result, 2)
        
        approach = self.grade_approaches.get(grade_level, self.grade_approaches["third_grade"])
        explanation = self._create_division_explanation(numbers, result, approach, grade_level)
        scene = self._create_division_scene(numbers, result, approach)
        
        final_answer = {
            "correct_value": str(result),
            "explanation": f"Dividing gives us {result}",
            "feedback_correct": "Excellent division work!",
            "feedback_incorrect": f"The correct answer is {result}."
        }
        
        if self.learning_tracker:
            self.learning_tracker.mark_topic_encountered("math")
            self.learning_tracker.log_interaction("math_division", text, f"Solved: {numbers[0]} ÷ {' ÷ '.join(str(n) for n in numbers[1:])} = {result}")
        
        return {
            "success": True,
            "response": explanation,
            "scene": scene,
            "final_answer": final_answer
        }
    
    def _create_addition_explanation(self, numbers: List[Union[int, float]], result: Union[int, float], 
                                   approach: Dict[str, Any], grade_level: str) -> str:
        """
        Create grade-appropriate addition explanation
        """
        if approach["simple_language"]:
            if len(numbers) == 2:
                explanation = f"Let's add {numbers[0]} and {numbers[1]} together!\n\n"
                
                if approach["use_objects"] and max(numbers) <= 10:
                    explanation += f"Imagine we have {numbers[0]} apples and we get {numbers[1]} more apples. "
                    explanation += f"Now we have {result} apples altogether!\n\n"
                
                explanation += f"So {numbers[0]} + {numbers[1]} = {result}"
            else:
                explanation = f"Let's add all these numbers: {', '.join(str(n) for n in numbers)}.\n\n"
                explanation += f"When we add them all together, we get {result}."
        else:
            explanation = f"Let's solve {' + '.join(str(n) for n in numbers)}.\n\n"
            if len(numbers) > 2:
                explanation += "We can add multiple numbers by combining their values step by step.\n\n"
            explanation += f"The sum of {' + '.join(str(n) for n in numbers)} is {result}."
        
        return explanation
    
    def _create_addition_scene(self, numbers: List[Union[int, float]], result: Union[int, float], 
                             approach: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create visual scene for addition
        """
        scene = []
        x_position = 100
        
        # Add the equation
        for i, num in enumerate(numbers):
            scene.append({
                "id": f"num-{i}",
                "type": "text",
                "x": x_position,
                "y": 150,
                "text": str(int(num) if num == int(num) else num),
                "fontSize": 32,
                "fontFamily": "Arial"
            })
            x_position += 60
            
            if i < len(numbers) - 1:
                scene.append({
                    "id": f"plus-{i}",
                    "type": "text",
                    "x": x_position,
                    "y": 150,
                    "text": "+",
                    "fontSize": 32,
                    "fontFamily": "Arial"
                })
                x_position += 40
        
        # Add equals and result
        scene.append({
            "id": "equals",
            "type": "text",
            "x": x_position,
            "y": 150,
            "text": "=",
            "fontSize": 32,
            "fontFamily": "Arial"
        })
        
        scene.append({
            "id": "result",
            "type": "text",
            "x": x_position + 40,
            "y": 150,
            "text": str(int(result) if result == int(result) else result),
            "fontSize": 32,
            "fontFamily": "Arial"
        })
        
        # Add visual objects for young students
        if approach["use_objects"] and len(numbers) == 2 and max(numbers) <= 10:
            y_pos = 250
            x_start = 100
            
            # First group of apples
            for i in range(int(numbers[0])):
                scene.append({
                    "id": f"apple-group1-{i}",
                    "type": "apple",
                    "x": x_start + (i * 50),
                    "y": y_pos,
                    "count": 1
                })
            
            # Second group of apples
            x_start += int(numbers[0]) * 50 + 80
            for i in range(int(numbers[1])):
                scene.append({
                    "id": f"apple-group2-{i}",
                    "type": "apple",
                    "x": x_start + (i * 50),
                    "y": y_pos,
                    "count": 1
                })
        
        return scene
    
    def _create_subtraction_explanation(self, numbers: List[Union[int, float]], result: Union[int, float], 
                                      approach: Dict[str, Any], grade_level: str) -> str:
        """
        Create grade-appropriate subtraction explanation
        """
        first_num = numbers[0]
        other_nums = numbers[1:]
        
        if approach["simple_language"]:
            if len(numbers) == 2:
                explanation = f"Let's start with {first_num} and take away {other_nums[0]}.\n\n"
                
                if approach["use_objects"] and first_num <= 10:
                    explanation += f"Imagine we have {first_num} cookies and we eat {other_nums[0]} of them. "
                    explanation += f"How many cookies do we have left? We have {result} cookies!\n\n"
                
                explanation += f"So {first_num} - {other_nums[0]} = {result}"
            else:
                explanation = f"Let's start with {first_num} and subtract the other numbers.\n\n"
                explanation += f"{first_num} - {' - '.join(str(n) for n in other_nums)} = {result}"
        else:
            explanation = f"Let's calculate {first_num} - {' - '.join(str(n) for n in other_nums)}.\n\n"
            explanation += f"When we subtract, we find what's left after taking away.\n\n"
            explanation += f"The result is {result}."
        
        return explanation
    
    def _create_subtraction_scene(self, numbers: List[Union[int, float]], result: Union[int, float], 
                                approach: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create visual scene for subtraction
        """
        scene = []
        x_position = 100
        
        # Add the equation
        scene.append({
            "id": "num-0",
            "type": "text",
            "x": x_position,
            "y": 150,
            "text": str(int(numbers[0]) if numbers[0] == int(numbers[0]) else numbers[0]),
            "fontSize": 32,
            "fontFamily": "Arial"
        })
        x_position += 60
        
        for i, num in enumerate(numbers[1:], 1):
            scene.append({
                "id": f"minus-{i}",
                "type": "text",
                "x": x_position,
                "y": 150,
                "text": "-",
                "fontSize": 32,
                "fontFamily": "Arial"
            })
            x_position += 40
            
            scene.append({
                "id": f"num-{i}",
                "type": "text",
                "x": x_position,
                "y": 150,
                "text": str(int(num) if num == int(num) else num),
                "fontSize": 32,
                "fontFamily": "Arial"
            })
            x_position += 60
        
        # Add equals and result
        scene.append({
            "id": "equals",
            "type": "text",
            "x": x_position,
            "y": 150,
            "text": "=",
            "fontSize": 32,
            "fontFamily": "Arial"
        })
        
        scene.append({
            "id": "result",
            "type": "text",
            "x": x_position + 40,
            "y": 150,
            "text": str(int(result) if result == int(result) else result),
            "fontSize": 32,
            "fontFamily": "Arial"
        })
        
        return scene
    
    def _create_multiplication_explanation(self, numbers: List[Union[int, float]], result: Union[int, float], 
                                         approach: Dict[str, Any], grade_level: str) -> str:
        """
        Create grade-appropriate multiplication explanation
        """
        if approach["simple_language"] and len(numbers) == 2:
            num1, num2 = numbers[0], numbers[1]
            explanation = f"Let's see what {num1} groups of {num2} looks like!\n\n"
            
            if approach["use_objects"] and max(numbers) <= 5:
                explanation += f"Imagine {num1} groups with {num2} items in each group.\n"
                explanation += f"If we count all the items, we get {result}!\n\n"
            
            explanation += f"So {num1} × {num2} = {result}"
        else:
            explanation = f"Let's calculate {' × '.join(str(n) for n in numbers)}.\n\n"
            explanation += f"Multiplication gives us the total when we have equal groups.\n\n"
            explanation += f"The product is {result}."
        
        return explanation
    
    def _create_multiplication_scene(self, numbers: List[Union[int, float]], result: Union[int, float], 
                                   approach: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create visual scene for multiplication
        """
        scene = []
        x_position = 100
        
        # Add the equation
        for i, num in enumerate(numbers):
            scene.append({
                "id": f"num-{i}",
                "type": "text",
                "x": x_position,
                "y": 150,
                "text": str(int(num) if num == int(num) else num),
                "fontSize": 32,
                "fontFamily": "Arial"
            })
            x_position += 60
            
            if i < len(numbers) - 1:
                scene.append({
                    "id": f"times-{i}",
                    "type": "text",
                    "x": x_position,
                    "y": 150,
                    "text": "×",
                    "fontSize": 32,
                    "fontFamily": "Arial"
                })
                x_position += 40
        
        # Add equals and result
        scene.append({
            "id": "equals",
            "type": "text",
            "x": x_position,
            "y": 150,
            "text": "=",
            "fontSize": 32,
            "fontFamily": "Arial"
        })
        
        scene.append({
            "id": "result",
            "type": "text",
            "x": x_position + 40,
            "y": 150,
            "text": str(int(result) if result == int(result) else result),
            "fontSize": 32,
            "fontFamily": "Arial"
        })
        
        return scene
    
    def _create_division_explanation(self, numbers: List[Union[int, float]], result: Union[int, float], 
                                   approach: Dict[str, Any], grade_level: str) -> str:
        """
        Create grade-appropriate division explanation
        """
        if approach["simple_language"] and len(numbers) == 2:
            dividend, divisor = numbers[0], numbers[1]
            explanation = f"Let's share {dividend} items equally among {divisor} groups.\n\n"
            
            if approach["use_objects"] and dividend <= 20 and divisor <= 5:
                explanation += f"If we have {dividend} cookies and share them equally among {divisor} friends, "
                explanation += f"each friend gets {result} cookies.\n\n"
            
            explanation += f"So {dividend} ÷ {divisor} = {result}"
        else:
            explanation = f"Let's calculate {' ÷ '.join(str(n) for n in numbers)}.\n\n"
            explanation += f"Division helps us find how many equal groups we can make.\n\n"
            explanation += f"The quotient is {result}."
        
        return explanation
    
    def _create_division_scene(self, numbers: List[Union[int, float]], result: Union[int, float], 
                             approach: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create visual scene for division
        """
        scene = []
        x_position = 100
        
        # Add the equation
        scene.append({
            "id": "num-0",
            "type": "text",
            "x": x_position,
            "y": 150,
            "text": str(int(numbers[0]) if numbers[0] == int(numbers[0]) else numbers[0]),
            "fontSize": 32,
            "fontFamily": "Arial"
        })
        x_position += 60
        
        for i, num in enumerate(numbers[1:], 1):
            scene.append({
                "id": f"divide-{i}",
                "type": "text",
                "x": x_position,
                "y": 150,
                "text": "÷",
                "fontSize": 32,
                "fontFamily": "Arial"
            })
            x_position += 40
            
            scene.append({
                "id": f"num-{i}",
                "type": "text",
                "x": x_position,
                "y": 150,
                "text": str(int(num) if num == int(num) else num),
                "fontSize": 32,
                "fontFamily": "Arial"
            })
            x_position += 60
        
        # Add equals and result
        scene.append({
            "id": "equals",
            "type": "text",
            "x": x_position,
            "y": 150,
            "text": "=",
            "fontSize": 32,
            "fontFamily": "Arial"
        })
        
        scene.append({
            "id": "result",
            "type": "text",
            "x": x_position + 40,
            "y": 150,
            "text": str(result),
            "fontSize": 32,
            "fontFamily": "Arial"
        })
        
        return scene
    
    def _extract_numbers(self, text: str) -> List[Union[int, float]]:
        """
        Extract numbers from text
        """
        # Pattern to match integers and decimals
        number_pattern = r'-?\d+\.?\d*'
        matches = re.findall(number_pattern, text)
        
        numbers = []
        for match in matches:
            try:
                if '.' in match:
                    numbers.append(float(match))
                else:
                    numbers.append(int(match))
            except ValueError:
                continue
        
        return numbers
    
    def _determine_grade_level(self, text: str, numbers: List[Union[int, float]]) -> str:
        """
        Determine appropriate grade level based on text and numbers
        """
        # Check for explicit grade mentions
        grade_patterns = [
            (r"kindergarten|k-?\d", "kindergarten"),
            (r"first|1st|grade 1", "first_grade"),
            (r"second|2nd|grade 2", "second_grade"),
            (r"third|3rd|grade 3", "third_grade"),
            (r"fourth|4th|grade 4", "fourth_grade"),
            (r"fifth|5th|grade 5", "fifth_grade"),
            (r"sixth|6th|grade 6", "sixth_grade")
        ]
        
        text_lower = text.lower()
        for pattern, grade in grade_patterns:
            if re.search(pattern, text_lower):
                return grade
        
        # Infer from number complexity
        if not numbers:
            return "third_grade"  # Default
        
        max_num = max(abs(n) for n in numbers)
        
        if max_num <= 10:
            return "kindergarten"
        elif max_num <= 20:
            return "first_grade"
        elif max_num <= 100:
            return "second_grade"
        elif max_num <= 1000:
            return "third_grade"
        elif max_num <= 10000:
            return "fourth_grade"
        else:
            return "fifth_grade"
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available math commands
        """
        return [
            "math_addition",
            "math_subtraction", 
            "math_multiplication",
            "math_division"
        ]