"""
PEARL AI Backend - Main Entry Point
Orchestrates all backend components for the AI tutor system
"""

from fastapi import FastAPI, UploadFile, File, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import uvicorn
import asyncio
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Import backend modules
from backend.core_agent import CoreAgent
from backend.speech_processor import SpeechProcessor, TTS_OUTPUT_DIR
from backend.camera_system import CameraSystem
from backend.emotion_analyzer import EmotionAnalyzer
from backend.rag_system import RAGSystem, RAG_DOCS_DIR
from backend.learning_tracker import LearningTracker
from backend.intent_classifier import IntentClassifier
from backend.commands.command_executor import CommandExecutor

# Request models
class TextRequest(BaseModel):
    text: str

class TTSRequest(BaseModel):
    text: str

# Initialize FastAPI app
app = FastAPI(title="PEARL AI Backend", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create required directories
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)
os.makedirs(RAG_DOCS_DIR, exist_ok=True)
os.makedirs("camera_captures", exist_ok=True)
os.makedirs("learning_data", exist_ok=True)

# Mount static files
app.mount("/tts_output", StaticFiles(directory=TTS_OUTPUT_DIR), name="tts_output")

# Global components - initialized on startup
core_agent: Optional[CoreAgent] = None
speech_processor: Optional[SpeechProcessor] = None
camera_system: Optional[CameraSystem] = None
emotion_analyzer: Optional[EmotionAnalyzer] = None
rag_system: Optional[RAGSystem] = None
learning_tracker: Optional[LearningTracker] = None
intent_classifier: Optional[IntentClassifier] = None
command_executor: Optional[CommandExecutor] = None

@app.on_event("startup")
async def startup_event():
    """Initialize all backend components on startup"""
    global core_agent, speech_processor, camera_system, emotion_analyzer
    global rag_system, learning_tracker, intent_classifier, command_executor
    
    print("Initializing PEARL AI Backend...")
    
    # Initialize core components
    try:
        # 1. Speech processor
        print("Initializing speech processor...")
        speech_processor = SpeechProcessor()
        
        # 2. Emotion analyzer
        print("Initializing emotion analyzer...")
        try:
            emotion_analyzer = EmotionAnalyzer()
            print("Emotion analyzer ready")
        except Exception as e:
            print(f"Warning: Emotion analyzer failed to initialize: {e}")
            emotion_analyzer = None
        
        # 3. Camera system (with emotion callback)
        print("Initializing camera system...")
        try:
            camera_system = CameraSystem(emotion_analyzer=emotion_analyzer)
            print("Camera system ready")
        except Exception as e:
            print(f"Warning: Camera system failed to initialize: {e}")
            camera_system = None
        
        # 4. RAG system
        print("Initializing RAG system...")
        rag_system = RAGSystem()
        print("RAG system ready")
        
        # 5. Learning tracker
        print("Initializing learning tracker...")
        learning_tracker = LearningTracker()
        print("Learning tracker ready")
        
        # 6. Intent classifier
        print("Initializing intent classifier...")
        intent_classifier = IntentClassifier()
        print("Intent classifier ready")
        
        # 7. Command executor
        print("Initializing command executor...")
        command_executor = CommandExecutor(
            camera_system=camera_system,
            learning_tracker=learning_tracker
        )
        print("Command executor ready")
        
        # 8. Core agent (main orchestrator)
        print("Initializing core agent...")
        core_agent = CoreAgent(
            speech_processor=speech_processor,
            emotion_analyzer=emotion_analyzer,
            camera_system=camera_system,
            rag_system=rag_system,
            learning_tracker=learning_tracker,
            intent_classifier=intent_classifier,
            command_executor=command_executor
        )
        print("Core agent ready")
        
        print("PEARL AI Backend initialization complete!")
        
    except Exception as e:
        print(f"Critical error during initialization: {e}")
        raise

# Health check endpoint
@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "message": "PEARL AI Backend is running",
        "components": {
            "core_agent": core_agent is not None,
            "speech_processor": speech_processor is not None,
            "camera_system": camera_system is not None,
            "emotion_analyzer": emotion_analyzer is not None,
            "rag_system": rag_system is not None,
            "learning_tracker": learning_tracker is not None,
            "intent_classifier": intent_classifier is not None,
            "command_executor": command_executor is not None
        }
    }

# Greeting endpoint - starts the interaction flow
@app.get("/greeting")
async def get_greeting():
    """Get initial greeting message and start the learning session"""
    if not core_agent:
        return {"error": "Core agent not initialized"}
    
    try:
        # Get personalized greeting based on learning history
        greeting_response = await core_agent.get_personalized_greeting()
        return greeting_response
    except Exception as e:
        print(f"Error getting greeting: {e}")
        return {"error": str(e)}

# Main speech processing endpoint
@app.post("/tutor/speak")
async def process_speech(file: UploadFile = File(...)):
    """Process speech input through the complete AI pipeline"""
    if not core_agent:
        return {"error": "Core agent not initialized"}
    
    try:
        print(f"Processing speech file: {file.filename}")
        
        # Read audio data
        audio_data = await file.read()
        
        # Process through core agent
        response = await core_agent.process_speech_input(audio_data)
        
        return response
        
    except Exception as e:
        print(f"Error processing speech: {e}")
        return {"error": str(e)}

# Text input endpoint
@app.post("/tutor/text")
async def process_text(request: TextRequest):
    """Process text input through the complete AI pipeline"""
    if not core_agent:
        return {"error": "Core agent not initialized"}
    
    try:
        print(f"Processing text: {request.text}")
        
        # Process through core agent
        response = await core_agent.process_text_input(request.text)
        
        return response
        
    except Exception as e:
        print(f"Error processing text: {e}")
        return {"error": str(e)}

# Whiteboard image processing
@app.post("/process_whiteboard_image")
async def process_whiteboard_image(request: Request):
    """Process whiteboard image with prompt"""
    if not core_agent:
        return {"error": "Core agent not initialized"}
    
    try:
        # Get prompt from header
        prompt = request.headers.get("X-Prompt", "What's in this image?")
        
        # Read image data
        image_data = await request.body()
        
        # Process through core agent
        response = await core_agent.process_whiteboard_image(image_data, prompt)
        
        return response
        
    except Exception as e:
        print(f"Error processing whiteboard image: {e}")
        return {"error": str(e)}

# Text-to-speech endpoint
@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Generate speech from text"""
    if not speech_processor:
        return {"error": "Speech processor not initialized"}
    
    try:
        audio_file = speech_processor.generate_speech(request.text)
        return {
            "message": "Speech generated successfully",
            "audio": f"/tts_output/{audio_file}"
        }
    except Exception as e:
        return {"error": str(e)}

# Camera control endpoints
@app.post("/camera/start")
async def start_camera():
    """Start the camera system"""
    if not camera_system:
        return {"error": "Camera system not available"}
    
    success = camera_system.start()
    return {
        "success": success,
        "message": "Camera started" if success else "Failed to start camera"
    }

@app.post("/camera/stop")
async def stop_camera():
    """Stop the camera system"""
    if not camera_system:
        return {"error": "Camera system not available"}
    
    success = camera_system.stop()
    return {
        "success": success,
        "message": "Camera stopped" if success else "Failed to stop camera"
    }

@app.post("/camera/capture")
async def capture_image():
    """Capture image from camera"""
    if not camera_system:
        return {"error": "Camera system not available"}
    
    try:
        result = camera_system.capture_image()
        return result if result else {"error": "Failed to capture image"}
    except Exception as e:
        return {"error": str(e)}

# Learning progress endpoints
@app.get("/learning/progress")
async def get_learning_progress():
    """Get current learning progress"""
    if not learning_tracker:
        return {"error": "Learning tracker not available"}
    
    try:
        progress = learning_tracker.get_current_progress()
        return progress
    except Exception as e:
        return {"error": str(e)}

@app.post("/learning/log_answer")
async def log_answer_result(request: dict):
    """Log student answer result"""
    if not learning_tracker:
        return {"error": "Learning tracker not available"}
    
    try:
        topic = request.get("topic", "math")
        is_correct = request.get("is_correct", False)
        difficulty = request.get("difficulty", "medium")
        
        learning_tracker.log_answer_result(topic, is_correct, difficulty)
        
        return {"message": "Answer result logged successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/learning/objectives")
async def get_learning_objectives():
    """Get current learning objectives"""
    if not learning_tracker:
        return {"error": "Learning tracker not available"}
    
    try:
        objectives = learning_tracker.get_active_objectives()
        return objectives
    except Exception as e:
        return {"error": str(e)}

@app.post("/learning/reset")
async def reset_learning_progress():
    """Reset learning progress"""
    if not learning_tracker:
        return {"error": "Learning tracker not available"}
    
    try:
        learning_tracker.reset_progress()
        return {"message": "Learning progress reset"}
    except Exception as e:
        return {"error": str(e)}

# RAG system endpoints
@app.get("/rag/documents")
async def get_documents():
    """Get list of documents in RAG system"""
    if not rag_system:
        return {"error": "RAG system not available"}
    
    try:
        return rag_system.get_document_list()
    except Exception as e:
        return {"error": str(e)}

@app.post("/rag/scan")
async def scan_documents():
    """Scan and update RAG documents"""
    if not rag_system:
        return {"error": "RAG system not available"}
    
    try:
        result = rag_system.scan_documents_folder()
        return result
    except Exception as e:
        return {"error": str(e)}

# WebSocket for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            if not core_agent:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Core agent not initialized"}
                })
                continue
            
            # Process message through core agent
            response = await core_agent.process_websocket_message(data)
            
            # Send response
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"message": str(e)}
            })
        except:
            pass

if __name__ == "__main__":
    print("Starting PEARL AI Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)