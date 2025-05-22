"""
Speech Processor
"""

import os
import re
import json
import time
import whisper
from TTS.api import TTS
import tempfile

TTS_OUTPUT_DIR = "tts_output"
TEMP_AUDIO_PATH = "temp_audio.wav"

class SpeechProcessor:
    
    def __init__(self):
        os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)
        
        try:
            self.stt_model = whisper.load_model("base")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.stt_model = None
        
        try:
            self.tts_model = TTS(model_name="tts_models/en/ljspeech/glow-tts", 
                               progress_bar=False, gpu=False)
        except Exception as e:
            print(f"Error loading TTS model: {e}")
            self.tts_model = None
    
    def transcribe_audio(self, audio_data: bytes = None, filepath: str = None) -> str:
        if self.stt_model is None:
            raise ValueError("Speech-to-text model not available")
        
        try:
            if audio_data is not None:
                with open(TEMP_AUDIO_PATH, "wb") as f:
                    f.write(audio_data)
                filepath = TEMP_AUDIO_PATH
            
            if filepath is None or not os.path.exists(filepath):
                raise ValueError("No audio data or valid filepath provided")
            
            result = self.stt_model.transcribe(filepath)
            transcription_text = result.get("text", "").strip()
            transcription_text = self._clean_transcription(transcription_text)
            
            if filepath == TEMP_AUDIO_PATH and os.path.exists(TEMP_AUDIO_PATH):
                try:
                    os.remove(TEMP_AUDIO_PATH)
                except:
                    pass
            
            return transcription_text
        except Exception as e:
            print(f"Error in transcription: {e}")
            raise
    
    def generate_speech(self, text: str) -> str:
        if self.tts_model is None:
            raise ValueError("Text-to-speech model not available")
        
        try:
            timestamp = int(time.time())
            output_filename = f"response_{timestamp}.wav"
            output_path = os.path.join(TTS_OUTPUT_DIR, output_filename)
            
            cleaned_text = self._clean_text_for_tts(text)
            self.tts_model.tts_to_file(text=cleaned_text, file_path=output_path)
            
            return output_filename
        except Exception as e:
            print(f"Error generating speech: {e}")
            raise
    
    def _clean_transcription(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'^(um|uh|like|so|well|okay|actually)\s+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+(um|uh|like|you know)$', '', text, flags=re.IGNORECASE)
        
        if text and not text[-1] in '.?!':
            text += '.'
        
        return text.strip()
    
    def _clean_text_for_tts(self, text: str) -> str:
        try:
            if text.startswith('{') and text.endswith('}'):
                try:
                    json_data = json.loads(text)
                    if 'explanation' in json_data:
                        text = json_data['explanation']
                except json.JSONDecodeError:
                    pass
            
            elif '```json' in text:
                json_start = text.find('```json') + 7
                json_end = text.rfind('```')
                if json_start > 0 and json_end > json_start:
                    json_str = text[json_start:json_end].strip()
                    try:
                        json_data = json.loads(json_str)
                        if 'explanation' in json_data:
                            text = json_data['explanation']
                    except json.JSONDecodeError:
                        pass
            
            cleaned_text = text.replace('\\', '').replace('```json', '').replace('```', '').strip()
            cleaned_text = re.sub(r'\[DRAW:.*?\]', '', cleaned_text).strip()
            cleaned_text = cleaned_text.replace('+', ' plus ').replace('=', ' equals ')
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            cleaned_text = re.sub(r'<[^>]+>', '', cleaned_text)
            
            if len(cleaned_text) > 1000:
                cleaned_text = cleaned_text[:997] + "..."
            
            return cleaned_text
        except Exception as e:
            print(f"Error cleaning text for TTS: {e}")
            return text[:500]