"""
Learning Tracker - Tracks student progress and learning history
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class LearningSession:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    topics_covered: List[str]
    interactions: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    emotion_data: List[Dict[str, Any]]

@dataclass
class TopicProgress:
    topic_name: str
    knowledge_level: str  # "beginner", "intermediate", "advanced"
    first_encountered: datetime
    last_studied: datetime
    total_time_spent: int  # in minutes
    correct_answers: int
    incorrect_answers: int
    concepts_mastered: List[str]
    struggling_areas: List[str]
    
@dataclass
class StudentProfile:
    student_id: str
    name: Optional[str]
    grade_level: Optional[str]
    learning_style: str  # "visual", "auditory", "kinesthetic"
    topics: Dict[str, TopicProgress]
    total_sessions: int
    total_learning_time: int  # in minutes
    strengths: List[str]
    areas_for_improvement: List[str]

class LearningTracker:
    """
    Tracks student learning progress, knowledge levels, and performance
    """
    
    def __init__(self, data_dir: str = "learning_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.current_session: Optional[LearningSession] = None
        self.student_profile: Optional[StudentProfile] = None
        
        # File paths
        self.profile_file = self.data_dir / "student_profile.json"
        self.sessions_file = self.data_dir / "sessions.json"
        self.temp_progress_file = self.data_dir / "temp_progress.json"
        
        # Load existing data
        self._load_student_profile()
        
        print("Learning Tracker initialized")
    
    def start_new_session(self) -> str:
        """
        Start a new learning session
        """
        session_id = f"session_{int(time.time())}"
        
        self.current_session = LearningSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            topics_covered=[],
            interactions=[],
            performance_metrics={
                "questions_asked": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "hints_used": 0,
                "topics_explored": 0
            },
            emotion_data=[]
        )
        
        print(f"Started new learning session: {session_id}")
        return session_id
    
    def end_current_session(self):
        """
        End the current learning session and save data
        """
        if not self.current_session:
            return
        
        self.current_session.end_time = datetime.now()
        
        # Calculate session duration
        duration = (self.current_session.end_time - self.current_session.start_time).total_seconds() / 60
        
        # Update student profile
        if self.student_profile:
            self.student_profile.total_sessions += 1
            self.student_profile.total_learning_time += int(duration)
            
            # Update topic progress
            for topic in self.current_session.topics_covered:
                if topic in self.student_profile.topics:
                    topic_progress = self.student_profile.topics[topic]
                    topic_progress.last_studied = datetime.now()
                    topic_progress.total_time_spent += int(duration / len(self.current_session.topics_covered))
        
        # Save session data
        self._save_session_data()
        self._save_student_profile()
        
        print(f"Ended session {self.current_session.session_id}, duration: {duration:.1f} minutes")
        self.current_session = None
    
    def log_interaction(self, interaction_type: str, input_text: str, response: Any):
        """
        Log a student interaction
        """
        if not self.current_session:
            self.start_new_session()
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,  # "command", "educational", "assessment"
            "input": input_text,
            "response": str(response),
            "success": True
        }
        
        self.current_session.interactions.append(interaction)
        self.current_session.performance_metrics["questions_asked"] += 1
        
        # Extract topic if possible
        topic = self._extract_topic_from_interaction(input_text)
        if topic and topic not in self.current_session.topics_covered:
            self.current_session.topics_covered.append(topic)
            self.current_session.performance_metrics["topics_explored"] += 1
    
    def log_answer_result(self, topic: str, is_correct: bool, difficulty: str = "medium"):
        """
        Log the result of a student answer
        """
        if not self.current_session:
            return
        
        if is_correct:
            self.current_session.performance_metrics["correct_answers"] += 1
        else:
            self.current_session.performance_metrics["incorrect_answers"] += 1
        
        # Update topic progress
        if not self.student_profile:
            self._create_default_profile()
        
        if topic not in self.student_profile.topics:
            self._create_topic_progress(topic)
        
        topic_progress = self.student_profile.topics[topic]
        if is_correct:
            topic_progress.correct_answers += 1
            # Add to strengths if performing well
            if topic_progress.correct_answers >= 3:
                accuracy = topic_progress.correct_answers / (topic_progress.correct_answers + topic_progress.incorrect_answers)
                if accuracy >= 0.75 and topic not in self.student_profile.strengths:
                    self.student_profile.strengths.append(topic)
                    # Remove from struggling areas if it was there
                    if topic in self.student_profile.areas_for_improvement:
                        self.student_profile.areas_for_improvement.remove(topic)
        else:
            topic_progress.incorrect_answers += 1
            # Add to struggling areas if having difficulty
            total_attempts = topic_progress.correct_answers + topic_progress.incorrect_answers
            if total_attempts >= 3:
                accuracy = topic_progress.correct_answers / total_attempts
                if accuracy < 0.5 and topic not in self.student_profile.areas_for_improvement:
                    self.student_profile.areas_for_improvement.append(topic)
                    # Remove from strengths if it was there
                    if topic in self.student_profile.strengths:
                        self.student_profile.strengths.remove(topic)
        
        # Update temporary progress file for real-time tracking
        self._save_temp_progress()
        self._save_student_profile()
    
    def mark_topic_encountered(self, topic: str):
        """
        Mark that a student has encountered a new topic
        """
        if not self.student_profile:
            self._create_default_profile()
        
        if topic not in self.student_profile.topics:
            self._create_topic_progress(topic)
        
        self._save_student_profile()
    
    def has_assessed_topic(self, topic: str) -> bool:
        """
        Check if we have assessed the student's knowledge of a topic
        """
        if not self.student_profile or topic not in self.student_profile.topics:
            return False
        
        topic_progress = self.student_profile.topics[topic]
        # Consider assessed if student has answered at least 2 questions
        return (topic_progress.correct_answers + topic_progress.incorrect_answers) >= 2
    
    def get_topic_knowledge(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Get student's knowledge level for a topic
        """
        if not self.student_profile or topic not in self.student_profile.topics:
            return None
        
        topic_progress = self.student_profile.topics[topic]
        total_answers = topic_progress.correct_answers + topic_progress.incorrect_answers
        
        if total_answers == 0:
            return {
                "level": "unknown",
                "performance": "no data",
                "needs_assessment": True
            }
        
        accuracy = topic_progress.correct_answers / total_answers
        
        # Determine knowledge level based on accuracy and number of attempts
        if accuracy >= 0.8 and total_answers >= 5:
            level = "advanced"
        elif accuracy >= 0.6 and total_answers >= 3:
            level = "intermediate"
        else:
            level = "beginner"
        
        return {
            "level": level,
            "performance": f"{accuracy:.1%} accuracy ({topic_progress.correct_answers}/{total_answers})",
            "struggling_areas": topic_progress.struggling_areas,
            "concepts_mastered": topic_progress.concepts_mastered,
            "needs_assessment": False
        }
    
    def get_topic_performance(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for a specific topic
        """
        if not self.student_profile or topic not in self.student_profile.topics:
            return None
        
        topic_progress = self.student_profile.topics[topic]
        return {
            "correct_answers": topic_progress.correct_answers,
            "incorrect_answers": topic_progress.incorrect_answers,
            "total_time": topic_progress.total_time_spent,
            "last_studied": topic_progress.last_studied.isoformat(),
            "struggling_areas": topic_progress.struggling_areas
        }
    
    def get_current_progress(self) -> Dict[str, Any]:
        """
        Get current learning progress summary
        """
        if not self.student_profile:
            return {
                "total_sessions": 0,
                "completed_topics": 0,
                "session_duration": 0,
                "struggling_areas": [],
                "last_topic": "",
                "learning_time": 0,
                "strengths": []
            }
        
        session_duration = 0
        if self.current_session:
            session_duration = (datetime.now() - self.current_session.start_time).total_seconds() / 60
        
        # Find most recently studied topic
        last_topic = ""
        latest_time = datetime.min
        for topic_name, topic_progress in self.student_profile.topics.items():
            if topic_progress.last_studied > latest_time:
                latest_time = topic_progress.last_studied
                last_topic = topic_name
        
        return {
            "total_sessions": self.student_profile.total_sessions,
            "completed_topics": len(self.student_profile.topics),
            "session_duration": int(session_duration),
            "struggling_areas": self.student_profile.areas_for_improvement,
            "last_topic": last_topic,
            "learning_time": self.student_profile.total_learning_time,
            "strengths": self.student_profile.strengths
        }
    
    def save_learning_objective(self, topic: str, objective: str, difficulty: str = "medium"):
        """
        Save a learning objective for temporary tracking
        """
        temp_data = self._load_temp_progress()
        
        if "learning_objectives" not in temp_data:
            temp_data["learning_objectives"] = []
        
        objective_data = {
            "topic": topic,
            "objective": objective,
            "difficulty": difficulty,
            "created_at": datetime.now().isoformat(),
            "completed": False
        }
        
        temp_data["learning_objectives"].append(objective_data)
        self._save_temp_progress_data(temp_data)
    
    def mark_objective_completed(self, objective: str):
        """
        Mark a learning objective as completed
        """
        temp_data = self._load_temp_progress()
        
        for obj in temp_data.get("learning_objectives", []):
            if obj["objective"] == objective:
                obj["completed"] = True
                obj["completed_at"] = datetime.now().isoformat()
                break
        
        self._save_temp_progress_data(temp_data)
    
    def get_active_objectives(self) -> List[Dict[str, Any]]:
        """
        Get currently active learning objectives
        """
        temp_data = self._load_temp_progress()
        return [obj for obj in temp_data.get("learning_objectives", []) if not obj.get("completed", False)]
    
    def reset_progress(self):
        """
        Reset all learning progress (for testing or new student)
        """
        self.student_profile = None
        self.current_session = None
        
        # Remove data files
        for file_path in [self.profile_file, self.sessions_file, self.temp_progress_file]:
            if file_path.exists():
                file_path.unlink()
        
        print("Learning progress reset")
    
    def _create_default_profile(self):
        """
        Create a default student profile
        """
        self.student_profile = StudentProfile(
            student_id=f"student_{int(time.time())}",
            name=None,
            grade_level=None,
            learning_style="visual",  # Default to visual
            topics={},
            total_sessions=0,
            total_learning_time=0,
            strengths=[],
            areas_for_improvement=[]
        )
    
    def _create_topic_progress(self, topic: str):
        """
        Create progress tracking for a new topic
        """
        if not self.student_profile:
            self._create_default_profile()
        
        self.student_profile.topics[topic] = TopicProgress(
            topic_name=topic,
            knowledge_level="unknown",
            first_encountered=datetime.now(),
            last_studied=datetime.now(),
            total_time_spent=0,
            correct_answers=0,
            incorrect_answers=0,
            concepts_mastered=[],
            struggling_areas=[]
        )
    
    def _extract_topic_from_interaction(self, text: str) -> Optional[str]:
        """
        Extract topic from interaction text
        """
        # Simple topic extraction - in a real system, this could be more sophisticated
        topic_keywords = {
            "math": ["math", "add", "subtract", "multiply", "divide", "number", "calculate"],
            "reading": ["read", "story", "book", "text", "comprehension"],
            "science": ["science", "experiment", "hypothesis", "theory"],
            "writing": ["write", "essay", "paragraph", "grammar"]
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        
        return None
    
    def _load_student_profile(self):
        """
        Load student profile from file
        """
        if not self.profile_file.exists():
            return
        
        try:
            with open(self.profile_file, 'r') as f:
                data = json.load(f)
            
            # Convert datetime strings back to datetime objects
            topics = {}
            for topic_name, topic_data in data.get("topics", {}).items():
                topic_data["first_encountered"] = datetime.fromisoformat(topic_data["first_encountered"])
                topic_data["last_studied"] = datetime.fromisoformat(topic_data["last_studied"])
                topics[topic_name] = TopicProgress(**topic_data)
            
            data["topics"] = topics
            self.student_profile = StudentProfile(**data)
            
            print(f"Loaded student profile: {self.student_profile.student_id}")
            
        except Exception as e:
            print(f"Error loading student profile: {e}")
    
    def _save_student_profile(self):
        """
        Save student profile to file
        """
        if not self.student_profile:
            return
        
        try:
            # Convert to dict and handle datetime serialization
            data = asdict(self.student_profile)
            
            # Convert datetime objects to strings
            for topic_name, topic_data in data["topics"].items():
                topic_data["first_encountered"] = topic_data["first_encountered"].isoformat()
                topic_data["last_studied"] = topic_data["last_studied"].isoformat()
            
            with open(self.profile_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving student profile: {e}")
    
    def _save_session_data(self):
        """
        Save current session data
        """
        if not self.current_session:
            return
        
        try:
            # Load existing sessions
            sessions = []
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r') as f:
                    sessions = json.load(f)
            
            # Convert current session to dict
            session_data = asdict(self.current_session)
            session_data["start_time"] = session_data["start_time"].isoformat()
            if session_data["end_time"]:
                session_data["end_time"] = session_data["end_time"].isoformat()
            
            # Add to sessions list
            sessions.append(session_data)
            
            # Keep only last 50 sessions
            sessions = sessions[-50:]
            
            # Save
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions, f, indent=2)
                
        except Exception as e:
            print(f"Error saving session data: {e}")
    
    def _load_temp_progress(self) -> Dict[str, Any]:
        """
        Load temporary progress data
        """
        if not self.temp_progress_file.exists():
            return {}
        
        try:
            with open(self.temp_progress_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading temp progress: {e}")
            return {}
    
    def _save_temp_progress(self):
        """
        Save temporary progress data
        """
        temp_data = self._load_temp_progress()
        
        # Update with current session info if available
        if self.current_session:
            temp_data["current_session"] = {
                "session_id": self.current_session.session_id,
                "start_time": self.current_session.start_time.isoformat(),
                "topics_covered": self.current_session.topics_covered,
                "performance": self.current_session.performance_metrics
            }
        
        self._save_temp_progress_data(temp_data)
    
    def _save_temp_progress_data(self, data: Dict[str, Any]):
        """
        Save temporary progress data to file
        """
        try:
            with open(self.temp_progress_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving temp progress: {e}")