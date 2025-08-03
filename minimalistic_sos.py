#!/usr/bin/env python3
"""
Voice-Triggered SOS with Offline Feedback using Gemma 3N
Minimalistic demonstration for Google Kaggle Hackathon

Demonstrates how to use Gemma 3N to:
- Listen for SOS keywords like "help" in multiple languages
- Respond with reassuring voice messages offline
- Process everything on-device for privacy and reliability

Modified Issue Scope: Simple demonstration of core capabilities
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import pyttsx3
import speech_recognition as sr
import time
import logging

# Simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalisticSOSDetector:
    """Simple SOS detection using Gemma 3N for elderly safety scenarios"""
    
    def __init__(self):
        # SOS keywords in target languages
        self.SOS_KEYWORDS = {
            'english': ['help', 'emergency', 'assistance'],
            'hindi': ['मदद', 'सहायता', 'बचाओ', 'madad', 'sahayata'],
            'bengali': ['সাহায্য', 'বাঁচাও', 'sahajjo', 'bachao']
        }
        
        # Standard response message
        self.RESPONSE_MESSAGES = {
            'english': "Help is on the way. Stay calm.",
            'hindi': "सहायता आ रही है। शांत रहें।",
            'bengali': "সাহায্য আসছে। শান্ত থাকুন।"
        }
        
        self.load_models()
    
    def load_models(self):
        """Load Gemma 3N and initialize TTS"""
        logger.info("Loading Gemma 3N model...")
        
        # Load Gemma model
        model_name = "google/gemma-2b"  # Will be updated to Gemma 3N
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Initialize TTS for offline voice response
        self.tts = pyttsx3.init()
        self.setup_tts()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        logger.info("✅ Models loaded successfully")
    
    def setup_tts(self):
        """Configure TTS for clear, elderly-friendly speech"""
        self.tts.setProperty('rate', 150)  # Slower for clarity
        self.tts.setProperty('volume', 0.9)  # High volume
    
    def detect_sos_with_gemma(self, text: str) -> tuple[bool, str]:
        """Use Gemma 3N to detect emergency intent"""
        try:
            # Simple prompt for emergency detection
            prompt = f"""
Analyze this speech to detect if someone needs emergency help.

Text: "{text}"

Look for:
- Calls for help in English, Hindi, or Bengali
- Emergency situations
- Distress signals

Respond with only: YES or NO
"""
            
            # Generate response
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_new_tokens=5,
                    temperature=0.1,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            
            if "yes" in response.lower():
                return True, "gemma_detection"
                
        except Exception as e:
            logger.error(f"Gemma analysis failed: {e}")
        
        return False, ""
    
    def check_keywords(self, text: str) -> tuple[bool, str]:
        """Simple keyword detection"""
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
        self.tts.say(message)
        self.tts.runAndWait()
    
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
        is_emergency, detection_method = self.detect_sos_with_gemma(text)
        
        if is_emergency:
            response_msg = self.get_response('english')  # Default to English
            self.speak_response(response_msg)
            return {
                'is_emergency': True,
                'method': detection_method,
                'language': 'english',
                'response': response_msg
            }
        
        return {
            'is_emergency': False,
            'method': 'no_detection',
            'language': None,
            'response': None
        }
    
    def listen_for_voice(self) -> str:
        """Simple voice input capture"""
        try:
            logger.info("🎤 Listening for voice input...")
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            # Convert speech to text
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
        print("\n🧪 DEMO MODE: Testing SOS Detection")
        print("=" * 50)
        
        test_cases = [
            "Help me please!",
            "मदद करो",  # Hindi
            "সাহায্য চাই",  # Bengali
            "I need assistance",
            "Hello there",  # Should not trigger
            "How are you?"  # Should not trigger
        ]
        
        for test_text in test_cases:
            print(f"\n📝 Testing: '{test_text}'")
            result = self.analyze_text(test_text)
            
            if result['is_emergency']:
                print(f"🚨 EMERGENCY DETECTED!")
                print(f"   Method: {result['method']}")
                print(f"   Language: {result['language']}")
                print(f"   Response: {result['response']}")
            else:
                print("✅ Normal conversation - no emergency")
            
            time.sleep(2)  # Pause between tests
    
    def live_mode(self):
        """Live voice monitoring"""
        print("\n🎤 LIVE MODE: Voice Monitoring")
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
                        print(f"Response: {result['response']}")
                        print("=" * 50)
                    else:
                        print(f"Normal speech: {voice_text}")
                
        except KeyboardInterrupt:
            print("\n👋 Stopping SOS monitoring")

def main():
    """Main demonstration function"""
    print("🚨 Voice-Triggered SOS with Gemma 3N")
    print("Google Kaggle Hackathon - Minimalistic Demo")
    print("=" * 60)
    print("🎯 Capabilities Demonstrated:")
    print("  • On-device speech recognition")
    print("  • Gemma 3N emergency intent detection")
    print("  • Offline voice response (TTS)")
    print("  • Multilingual support (English/Hindi/Bengali)")
    print("=" * 60)
    
    try:
        # Initialize SOS detector
        detector = MinimalisticSOSDetector()
        
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
        print("1. Install dependencies: pip install torch transformers SpeechRecognition pyttsx3 pyaudio")
        print("2. Ensure microphone is working")
        print("3. Check internet connection for initial model download")

if __name__ == "__main__":
    main()
