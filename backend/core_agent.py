"""
Core Agent - Main AI Orchestrator for PEARL
Handles the complete flow: greeting -> listen -> intent -> AI/command -> response -> follow-up
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, List, Optional, Union
import requests
from datetime import datetime

from backend.speech_processor import SpeechProcessor
from backend.emotion_analyzer import EmotionAnalyzer
from backend.camera_system import CameraSystem
from backend.rag_system import RAGSystem
from backend.learning_tracker import LearningTracker
from backend.intent_classifier import IntentClassifier
from backend.commands.command_executor import CommandExecutor

class CoreAgent:
    """
    Main AI orchestrator that manages the complete interaction flow
    """
    
    def __init__(self, 
                 speech_processor: SpeechProcessor,
                 emotion_analyzer: Optional[EmotionAnalyzer],
                 camera_system: Optional[CameraSystem],
                 rag_system: RAGSystem,
                 learning_tracker: LearningTracker,
                 intent_classifier: IntentClassifier,
                 command_executor: CommandExecutor):
        
        self.speech_processor = speech_processor
        self.emotion_analyzer = emotion_analyzer
        self.camera_system = camera_system
        self.rag_system = rag_system
        self.learning_tracker = learning_tracker
        self.intent_classifier = intent_classifier
        self.command_executor = command_executor
        
        # OpenRouter API configuration
        self.openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.llm_model = "meta-llama/llama-4-maverick:free"
        
        # System prompt for the AI
        self.system_prompt = """
        You are PEARL, a Personal Educational Assistant for Research and Learning.
        You are an intelligent, adaptive tutor that helps students learn effectively.
        
        Key behaviors:
        1. Always assess student knowledge before teaching new concepts
        2. Adapt your teaching style based on student responses and emotions
        3. Use grade-appropriate language and examples
        4. Provide step-by-step explanations for complex topics
        5. Ask follow-up questions to check understanding
        6. Encourage and motivate students
        7. Connect new learning to previously learned concepts
        
        When responding, structure your answer as JSON:
        {
            "explanation": "Your teaching explanation here",
            "scene": [array of visual elements to display],
            "final_answer": {
                "correct_value": "expected answer if this is a problem",
                "explanation": "why this is the answer",
                "feedback_correct": "positive feedback",
                "feedback_incorrect": "corrective feedback"
            },
            "follow_up_question": "Question to check understanding or continue learning",
            "knowledge_check": "What to assess about student knowledge"
        }
        """
        
        # Conversation state
        self.conversation_history = []
        self.current_session = {
            "start_time": datetime.now(),
            "topics_covered": [],
            "student_responses": [],
            "current_topic": None,
            "learning_objectives": []
        }
        
        print("Core Agent initialized successfully")
    
    async def get_personalized_greeting(self) -> Dict[str, Any]:
        """
        Generate a personalized greeting based on learning history and start camera/emotion detection
        """
        try:
            # Start camera system if available
            if self.camera_system and not self.camera_system.is_running:
                self.camera_system.start()
                print("Camera system started for emotion detection")
            
            # Get learning progress
            progress = self.learning_tracker.get_current_progress()
            
            # Generate personalized greeting
            if progress.get("total_sessions", 0) == 0:
                greeting = ("Hello! I'm PEARL, your Personal Educational Assistant for Research and Learning. "
                          "I'm here to help you learn and understand new concepts. "
                          "What would you like to learn about today?")
            else:
                last_topic = progress.get("last_topic", "")
                greeting = (f"Welcome back! Last time we were working on {last_topic}. "
                          f"You've completed {progress.get('completed_topics', 0)} topics so far. "
                          f"Would you like to continue with {last_topic} or start something new?")
            
            # Generate TTS audio
            audio_file = self.speech_processor.generate_speech(greeting)
            
            # Start new learning session
            self.learning_tracker.start_new_session()
            
            return {
                "greeting": greeting,
                "audio": f"/tts_output/{audio_file}",
                "session_id": self.current_session["start_time"].isoformat()
            }
            
        except Exception as e:
            print(f"Error generating greeting: {e}")
            return {"error": str(e)}
    
    async def process_speech_input(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process speech input through the complete AI pipeline
        """
        try:
            # 1. Transcribe speech
            print("Transcribing speech...")
            transcript = self.speech_processor.transcribe_audio(audio_data)
            print(f"Transcript: {transcript}")
            
            # 2. Process the transcript
            response = await self.process_text_input(transcript)
            
            # 3. Add audio to response if not already present
            if "audio" not in response and "explanation" in response.get("answer", {}):
                explanation = response["answer"]["explanation"]
                audio_file = self.speech_processor.generate_speech(explanation)
                response["audio"] = f"/tts_output/{audio_file}"
            
            return response
            
        except Exception as e:
            print(f"Error processing speech input: {e}")
            return self._create_error_response(f"Error processing speech: {str(e)}")
    
    async def process_text_input(self, text: str) -> Dict[str, Any]:
        """
        Process text input through the complete AI pipeline
        """
        try:
            print(f"Processing text input: {text}")
            
            # 1. Classify intent
            intent_result = self.intent_classifier.classify_intent(text)
            intent_type = intent_result["intent"]
            confidence = intent_result["confidence"]
            
            print(f"Classified intent: {intent_type} (confidence: {confidence})")
            
            # 2. Handle based on intent
            if intent_type == "command" and confidence > 0.7:
                # Execute command directly
                return await self._handle_command(text, intent_result)
            else:
                # Process as educational query
                return await self._handle_educational_query(text, intent_result)
                
        except Exception as e:
            print(f"Error processing text input: {e}")
            return self._create_error_response(f"Error processing input: {str(e)}")
    
    async def _handle_command(self, text: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle command execution
        """
        try:
            print("Executing command...")
            
            # Execute command
            command_result = self.command_executor.execute_command(text, intent_result)
            
            if command_result["success"]:
                # Log command execution
                self.learning_tracker.log_interaction("command", text, command_result["response"])
                
                return {
                    "question": text,
                    "answer": {
                        "explanation": command_result["response"],
                        "scene": command_result.get("scene", []),
                        "final_answer": command_result.get("final_answer", {})
                    },
                    "type": "command"
                }
            else:
                # Command failed, fall back to AI processing
                print("Command execution failed, falling back to AI processing")
                return await self._handle_educational_query(text, intent_result)
                
        except Exception as e:
            print(f"Error handling command: {e}")
            return await self._handle_educational_query(text, intent_result)
    
    async def _handle_educational_query(self, text: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle educational queries through AI processing
        """
        try:
            print("Processing as educational query...")
            
            # 1. Get emotion data for adaptive teaching
            emotion_data = self._get_current_emotion()
            
            # 2. Check if we need to assess student knowledge
            knowledge_assessment = await self._assess_knowledge_if_needed(text)
            
            # 3. Enhance query with RAG if relevant
            enhanced_query, rag_docs = self._enhance_with_rag(text)
            
            # 4. Build context for AI
            context = self._build_ai_context(text, emotion_data, knowledge_assessment, rag_docs)
            
            # 5. Query AI
            ai_response = await self._query_llm(enhanced_query, context)
            
            # 6. Process AI response
            processed_response = self._process_ai_response(ai_response, text)
            
            # 7. Update learning tracker
            self.learning_tracker.log_interaction("educational", text, processed_response)
            
            # 8. Save learning objectives if this is a new topic
            if knowledge_assessment and knowledge_assessment.get("needs_assessment"):
                topic = knowledge_assessment.get("topic")
                if topic:
                    objective = f"Learn basic concepts of {topic}"
                    difficulty = "easy" if "kindergarten" in text.lower() or "first" in text.lower() else "medium"
                    self.learning_tracker.save_learning_objective(topic, objective, difficulty)
            
            # 9. Check if follow-up is needed
            follow_up = self._generate_follow_up(processed_response, text)
            if follow_up:
                processed_response["follow_up"] = follow_up
            
            return processed_response
            
        except Exception as e:
            print(f"Error handling educational query: {e}")
            return self._create_error_response(f"Error processing educational query: {str(e)}")
    
    async def _assess_knowledge_if_needed(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Assess student knowledge if we're dealing with a new topic
        """
        try:
            # Extract topic from text
            topic = self.intent_classifier.extract_topic(text)
            
            if not topic:
                return None
            
            # Check if we've assessed this topic before
            if not self.learning_tracker.has_assessed_topic(topic):
                print(f"New topic detected: {topic}. Need to assess knowledge.")
                
                # Create knowledge assessment
                assessment = {
                    "topic": topic,
                    "needs_assessment": True,
                    "suggested_questions": [
                        f"Before we start with {topic}, can you tell me what you already know about it?",
                        f"Have you studied {topic} before?",
                        f"What grade level are you at?"
                    ]
                }
                
                # Mark topic as encountered
                self.learning_tracker.mark_topic_encountered(topic)
                
                return assessment
            
            # Get existing knowledge level
            return self.learning_tracker.get_topic_knowledge(topic)
            
        except Exception as e:
            print(f"Error assessing knowledge: {e}")
            return None
    
    def _enhance_with_rag(self, text: str) -> tuple:
        """
        Enhance query with RAG system if relevant documents are found
        """
        try:
            # Search for relevant documents
            relevant_docs = self.rag_system.retrieve(text, top_k=3)
            
            if not relevant_docs:
                return text, []
            
            # Build enhanced query with context
            context_parts = ["RELEVANT INFORMATION FROM KNOWLEDGE BASE:"]
            
            for doc, score in relevant_docs:
                if score > 0.7:  # Only use highly relevant documents
                    context_parts.append(f"- {doc.title}: {doc.content[:500]}...")
            
            if len(context_parts) > 1:
                enhanced_query = "\n".join(context_parts) + f"\n\nSTUDENT QUESTION: {text}"
                return enhanced_query, [doc.title for doc, _ in relevant_docs]
            
            return text, []
            
        except Exception as e:
            print(f"Error enhancing with RAG: {e}")
            return text, []
    
    def _build_ai_context(self, text: str, emotion_data: Optional[Dict], 
                         knowledge_assessment: Optional[Dict], rag_docs: List[str]) -> str:
        """
        Build context for AI based on student state and learning history
        """
        context_parts = [self.system_prompt]
        
        # Add emotion context
        if emotion_data and emotion_data.get("face_detected"):
            emotion = emotion_data["emotions"]["primary"]
            stress_level = emotion_data["emotions"]["stress_level"]
            
            context_parts.append(f"\nSTUDENT EMOTIONAL STATE:")
            context_parts.append(f"- Current emotion: {emotion}")
            context_parts.append(f"- Stress level: {stress_level:.2f}")
            
            if stress_level > 0.7:
                context_parts.append("- IMPORTANT: Student appears stressed. Use calming, supportive language and break down concepts into smaller steps.")
            elif stress_level < 0.3:
                context_parts.append("- Student appears relaxed and ready to learn.")
        
        # Add knowledge assessment context
        if knowledge_assessment:
            context_parts.append(f"\nKNOWLEDGE ASSESSMENT:")
            if knowledge_assessment.get("needs_assessment"):
                context_parts.append(f"- This is a new topic ({knowledge_assessment['topic']}) for the student")
                context_parts.append("- You should ask about their background knowledge before teaching")
            else:
                context_parts.append(f"- Student knowledge level: {knowledge_assessment.get('level', 'unknown')}")
                context_parts.append(f"- Previous performance: {knowledge_assessment.get('performance', 'no data')}")
        
        # Add learning history context
        progress = self.learning_tracker.get_current_progress()
        if progress:
            context_parts.append(f"\nLEARNING HISTORY:")
            context_parts.append(f"- Topics covered: {progress.get('completed_topics', 0)}")
            context_parts.append(f"- Current session duration: {progress.get('session_duration', 0)} minutes")
            
            if progress.get("struggling_areas"):
                context_parts.append(f"- Areas student struggles with: {', '.join(progress['struggling_areas'])}")
        
        # Add RAG document context
        if rag_docs:
            context_parts.append(f"\nRELEVANT KNOWLEDGE BASE DOCUMENTS: {', '.join(rag_docs)}")
        
        return "\n".join(context_parts)
    
    async def _query_llm(self, query: str, context: str) -> str:
        """
        Query the LLM with enhanced context
        """
        if not self.openrouter_api_key:
            return self._get_mock_response(query)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "PEARL AI Tutor",
                "Content-Type": "application/json",
            }
            
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": query}
            ]
            
            # Add recent conversation history
            if self.conversation_history:
                recent_history = self.conversation_history[-6:]  # Last 3 exchanges
                messages = [messages[0]] + recent_history + [messages[1]]
            
            payload = {
                "model": self.llm_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    ai_response = result["choices"][0]["message"]["content"]
                    
                    # Update conversation history
                    self.conversation_history.append({"role": "user", "content": query})
                    self.conversation_history.append({"role": "assistant", "content": ai_response})
                    
                    return ai_response
            
            return f"Error from AI service: {response.status_code}"
            
        except Exception as e:
            print(f"Error querying LLM: {e}")
            return f"Error communicating with AI: {str(e)}"
    
    def _get_mock_response(self, query: str) -> str:
        """
        Generate mock response when no API key is available
        """
        return json.dumps({
            "explanation": f"I understand you're asking about: {query}. This is a mock response since no OpenRouter API key is configured.",
            "scene": [],
            "final_answer": {
                "correct_value": "",
                "explanation": "Mock response - no actual calculation performed",
                "feedback_correct": "Good job!",
                "feedback_incorrect": "Let's try again"
            },
            "follow_up_question": "Would you like to learn more about this topic?",
            "knowledge_check": "basic understanding"
        })
    
    def _process_ai_response(self, ai_response: str, original_text: str) -> Dict[str, Any]:
        """
        Process and structure the AI response
        """
        try:
            # Try to parse as JSON first
            if ai_response.strip().startswith('{') and ai_response.strip().endswith('}'):
                try:
                    parsed_response = json.loads(ai_response)
                    
                    # Structure the response
                    return {
                        "question": original_text,
                        "answer": {
                            "explanation": parsed_response.get("explanation", ai_response),
                            "scene": parsed_response.get("scene", []),
                            "final_answer": parsed_response.get("final_answer", {})
                        },
                        "follow_up_question": parsed_response.get("follow_up_question"),
                        "knowledge_check": parsed_response.get("knowledge_check"),
                        "type": "educational"
                    }
                except json.JSONDecodeError:
                    pass
            
            # Handle non-JSON response
            return {
                "question": original_text,
                "answer": {
                    "explanation": ai_response,
                    "scene": [],
                    "final_answer": {}
                },
                "type": "educational"
            }
            
        except Exception as e:
            print(f"Error processing AI response: {e}")
            return self._create_error_response(f"Error processing AI response: {str(e)}")
    
    def _generate_follow_up(self, response: Dict[str, Any], original_text: str) -> Optional[str]:
        """
        Generate appropriate follow-up question based on the response and learning progress
        """
        try:
            # If response already has a follow-up, use it
            if response.get("follow_up_question"):
                return response["follow_up_question"]
            
            # Generate based on topic and student performance
            topic = self.intent_classifier.extract_topic(original_text)
            if topic:
                performance = self.learning_tracker.get_topic_performance(topic)
                
                if performance and performance.get("correct_answers", 0) >= 3:
                    return f"Great job with {topic}! Are you ready to try a more challenging problem?"
                elif performance and performance.get("incorrect_answers", 0) >= 2:
                    return f"Let's practice {topic} a bit more. Would you like me to explain it differently?"
                else:
                    return f"Do you have any questions about {topic}?"
            
            return "What would you like to learn about next?"
            
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            return None
    
    def _get_current_emotion(self) -> Optional[Dict[str, Any]]:
        """
        Get current emotion data from emotion analyzer
        """
        try:
            if not self.emotion_analyzer or not self.camera_system:
                return None
            
            if not self.camera_system.is_running:
                return None
            
            # Get latest frame from camera
            frame = self.camera_system.get_latest_frame()
            if frame is None:
                return None
            
            # Analyze emotion
            emotion_data = self.emotion_analyzer.analyze_frame(frame)
            return emotion_data
            
        except Exception as e:
            print(f"Error getting emotion data: {e}")
            return None
    
    async def process_whiteboard_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """
        Process whiteboard image with AI vision
        """
        try:
            # This would integrate with vision AI
            # For now, return a structured response
            return {
                "response": f"I can see your whiteboard. You asked: {prompt}. Let me analyze what you've drawn and help you with it.",
                "audio": None  # TTS will be added by the endpoint
            }
            
        except Exception as e:
            print(f"Error processing whiteboard image: {e}")
            return {"error": str(e)}
    
    async def process_websocket_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process WebSocket messages
        """
        try:
            message_type = data.get("type")
            
            if message_type == "text":
                response = await self.process_text_input(data.get("text", ""))
                return {"type": "response", "data": response}
            
            elif message_type == "command":
                command_result = self.command_executor.execute_command(
                    data.get("command", ""), 
                    data.get("args", {})
                )
                return {"type": "command_result", "data": command_result}
            
            else:
                return {"type": "error", "data": {"message": f"Unknown message type: {message_type}"}}
                
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")
            return {"type": "error", "data": {"message": str(e)}}
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create standardized error response
        """
        return {
            "question": "",
            "answer": {
                "explanation": error_message,
                "scene": [],
                "final_answer": {}
            },
            "error": True
        }