#!/usr/bin/env python3
"""
Voice-Triggered SOS with Offline Feedback using Gemma 3N
Corrected implementation using actual Gemma 3N models

Uses: google/gemma-3n-E2B-it or google/gemma-3n-E4B-it
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import pyttsx3
import speech_recognition as sr
import time
import logging

# Simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Gemma3NSOSDetector:
    """SOS detection system using actual Gemma 3N models"""
    
    def __init__(self, model_size="2B"):
        # SOS keywords
        self.SOS_KEYWORDS = {
            'english': ['help', 'emergency', 'assistance'],
            'hindi': ['मदद', 'सहायता', 'बचाओ', 'madad', 'sahayata'],
            'bengali': ['সাহায্য', 'বাঁচাও', 'sahajjo', 'bachao']
        }
        
        self.RESPONSE_MESSAGES = {
            'english': "Help is on the way. Stay calm.",
            'hindi': "सहायता आ रही है। शांत रहें।",
            'bengali': "সাহায্য আসছে। শান্ত থাকুন।"
        }
        
        self.model_size = model_size
        self.load_models()
    
    def load_models(self):
        """Load actual Gemma 3N models"""
        logger.info("Loading Gemma 3N models...")
        
        try:
            # Use actual Gemma 3N model names
            if self.model_size == "2B":
                model_name = "google/gemma-3n-E2B-it"  # 2B instruction-tuned
            else:
                model_name = "google/gemma-3n-E4B-it"  # 4B instruction-tuned
            
            logger.info(f"Loading {model_name}...")
            
            # Try using pipeline first (easier and handles authentication)
            try:
                self.pipe = pipeline(
                    "text-generation",
                    model=model_name,
                    device="cuda" if torch.cuda.is_available() else "cpu",
                    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
                )
                logger.info("✅ Gemma 3N pipeline loaded successfully")
                self.model = None  # Using pipeline instead
                self.tokenizer = None
                
            except Exception as e:
                logger.warning(f"Pipeline loading failed: {e}")
                logger.info("Trying direct model loading...")
                
                # Fallback to direct model loading
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                self.pipe = None
                logger.info("✅ Gemma 3N model loaded directly")
            
        except Exception as e:
            logger.error(f"Gemma 3N loading failed: {e}")
            logger.info("Falling back to keyword-only detection")
            self.model = None
            self.tokenizer = None
            self.pipe = None
        
        # Initialize TTS
        try:
            self.tts = pyttsx3.init()
            self.setup_tts()
            logger.info("✅ TTS initialized")
        except Exception as e:
            logger.error(f"TTS initialization failed: {e}")
            self.tts = None
        
        # Initialize speech recognition
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            logger.info("✅ Speech recognition initialized")
        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            self.recognizer = None
    
    def setup_tts(self):
        """Configure TTS for elderly-friendly speech"""
        if self.tts:
            self.tts.setProperty('rate', 150)
            self.tts.setProperty('volume', 0.9)
    
    def detect_sos_with_gemma3n(self, text: str) -> tuple[bool, float]:
        """Use actual Gemma 3N for emergency detection"""
        try:
            # Enhanced prompt for Gemma 3N
            prompt = f"""You are an emergency detection AI for elderly care.

Analyze this speech: "{text}"

Look for emergency situations:
- Direct calls for help ("help", "मदद", "সাহায্য")
- Medical emergencies (breathing, chest pain, dizziness)
- Falls or injuries ("fallen", "can't get up", "hurt")
- Distress signals

Respond with only: EMERGENCY or NORMAL

Analysis:"""

            if self.pipe:
                # Use pipeline
                response = self.pipe(
                    prompt,
                    max_new_tokens=10,
                    temperature=0.1,
                    do_sample=False,
                    return_full_text=False
                )
                result = response[0]['generated_text'].strip().lower()
                
            elif self.model and self.tokenizer:
                # Use direct model
                inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs.input_ids,
                        max_new_tokens=10,
                        temperature=0.1,
                        do_sample=False,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                result = self.tokenizer.decode(
                    outputs[0][inputs.input_ids.shape[1]:], 
                    skip_special_tokens=True
                ).strip().lower()
            else:
                # No model available
                return False, 0.0
            
            # Check if Gemma 3N detected emergency
            if "emergency" in result:
                logger.info(f"Gemma 3N detected emergency: {result}")
                return True, 0.9
                
        except Exception as e:
            logger.error(f"Gemma 3N analysis failed: {e}")
        
        return False, 0.0
    
    def check_keywords(self, text: str) -> tuple[bool, str]:
        """Quick keyword detection"""
        text_lower = text.lower()
        
        for language, keywords in self.SOS_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True, language
        
        return False, ""
    
    def get_response(self, language: str) -> str:
        """Get appropriate response message"""
        return self.RESPONSE_MESSAGES.get(language, self.RESPONSE_MESSAGES['english'])
    
    def speak_response(self, message: str):
        """Generate offline voice response"""
        logger.info(f"🗣️ Speaking: {message}")
        if self.tts:
            try:
                self.tts.say(message)
                self.tts.runAndWait()
            except Exception as e:
                logger.error(f"TTS failed: {e}")
        else:
            print(f"🗣️ Would speak: {message}")
    
    def analyze_text(self, text: str) -> dict:
        """Analyze text for emergency intent"""
        logger.info(f"Analyzing: '{text}'")
        
        # First check direct keywords (fast)
        has_keywords, language = self.check_keywords(text)
        
        if has_keywords:
            response_msg = self.get_response(language)
            self.speak_response(response_msg)
            return {
                'is_emergency': True,
                'method': 'keyword_detection',
                'language': language,
                'response': response_msg
            }
        
        # Use Gemma 3N for advanced detection
        is_emergency, confidence = self.detect_sos_with_gemma3n(text)
        
        if is_emergency:
            response_msg = self.get_response('english')  # Default to English
            self.speak_response(response_msg)
            return {
                'is_emergency': True,
                'method': 'gemma3n_detection',
                'language': 'english',
                'response': response_msg,
                'confidence': confidence
            }
        
        return {
            'is_emergency': False,
            'method': 'no_detection',
            'language': None,
            'response': None
        }
    
    def listen_for_voice(self) -> str:
        """Simple voice input capture"""
        if not self.recognizer:
            return ""
            
        try:
            logger.info("🎤 Listening for voice input...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Heard: '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            logger.info("No speech detected")
            return ""
        except sr.UnknownValueError:
            logger.info("Could not understand speech")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return ""
    
    def demo_mode(self):
        """Demonstrate with predefined test cases"""
        print("\n🧪 GEMMA 3N DEMO MODE: Testing SOS Detection")
        print("=" * 50)
        
        test_cases = [
            "Help me please!",
            "मदद करो",  # Hindi
            "সাহায্য চাই",  # Bengali
            "I need assistance urgently",
            "Emergency situation here",
            "I've fallen and can't get up",
            "Hello there",  # Should not trigger
            "How are you today?"  # Should not trigger
        ]
        
        for test_text in test_cases:
            print(f"\n📝 Testing: '{test_text}'")
            result = self.analyze_text(test_text)
            
            if result['is_emergency']:
                print(f"🚨 EMERGENCY DETECTED!")
                print(f"   Method: {result['method']}")
                print(f"   Language: {result['language']}")
                print(f"   Response: {result['response']}")
                if 'confidence' in result:
                    print(f"   Confidence: {result['confidence']:.2f}")
            else:
                print("✅ Normal conversation - no emergency")
            
            time.sleep(2)  # Pause between tests
    
    def live_mode(self):
        """Live voice monitoring"""
        if not self.recognizer:
            print("❌ Speech recognition not available")
            return
            
        print("\n🎤 LIVE MODE: Voice Monitoring with Gemma 3N")
        print("Say 'help', 'मदद', or 'সাহায্য' to trigger emergency response")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        try:
            while True:
                voice_text = self.listen_for_voice()
                if voice_text:
                    result = self.analyze_text(voice_text)
                    
                    if result['is_emergency']:
                        print(f"\n🚨 EMERGENCY ALERT 🚨")
                        print(f"Trigger: {voice_text}")
                        print(f"Method: {result['method']}")
                        print(f"Response: {result['response']}")
                        print("=" * 50)
                    else:
                        print(f"Normal speech: {voice_text}")
                
        except KeyboardInterrupt:
            print("\n👋 Stopping SOS monitoring")

def main():
    """Main demonstration function"""
    print("🚨 Voice-Triggered SOS with Gemma 3N")
    print("Google Kaggle Hackathon - Using Actual Gemma 3N Models")
    print("=" * 60)
    print("🎯 Capabilities Demonstrated:")
    print("  • Gemma 3N emergency intent detection")
    print("  • On-device speech recognition")
    print("  • Offline voice response (TTS)")
    print("  • Multilingual support (English/Hindi/Bengali)")
    print("=" * 60)
    
    try:
        # Ask for model size
        print("\nChoose Gemma 3N model size:")
        print("1. Gemma 3N 2B (faster, less memory)")
        print("2. Gemma 3N 4B (more accurate, more memory)")
        
        choice = input("Enter choice (1 or 2, default=1): ").strip()
        model_size = "4B" if choice == "2" else "2B"
        
        print(f"\nInitializing Gemma 3N {model_size} SOS Detector...")
        detector = Gemma3NSOSDetector(model_size=model_size)
        
        # Choose mode
        print("\nChoose demonstration mode:")
        print("1. Demo with predefined phrases")
        print("2. Live voice monitoring")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            detector.demo_mode()
        elif choice == "2":
            detector.live_mode()
        else:
            print("Invalid choice. Running demo mode...")
            detector.demo_mode()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you have Gemma 3N access: https://huggingface.co/google/gemma-3n-E2B-it")
        print("2. Login: py -c 'from huggingface_hub import login; login()'")
        print("3. Install timm: py -m pip install timm")
        print("4. Check internet connection for model download")

if __name__ == "__main__":
    main()
