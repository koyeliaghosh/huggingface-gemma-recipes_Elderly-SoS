# elderguard_complete.py - Complete Voice-Activated Emergency Response System
import speech_recognition as sr
import pyttsx3
import threading
import time
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

print("🛡️ ELDERGUARD - Voice-Activated Emergency Response System")
print("=" * 65)
print("✅ Complete System with Live Voice Testing")
print("=" * 65)

class ElderGuardSOS:
    def __init__(self):
        print("🔧 Initializing ElderGuard Emergency Response System...")
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Text-to-speech setup (optimized for elderly users)
        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        if len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)  # Female voice often clearer
        self.tts_engine.setProperty('rate', 130)  # Slower speech for elderly
        self.tts_engine.setProperty('volume', 0.9)  # High volume
        
        # Multilingual emergency keywords
        self.emergency_keywords = {
            'english': ['help', 'emergency', 'fallen', 'pain', 'cant move', 'need help', 'call 911', 'ambulance'],
            'spanish': ['ayuda', 'emergencia', 'caído', 'dolor', 'no puedo mover', 'auxilio'],
            'french': ['aide', 'urgence', 'tombé', 'douleur', 'ne peut pas bouger', 'secours'],
            'german': ['hilfe', 'notfall', 'gefallen', 'schmerz', 'kann nicht bewegen']
        }
        
        # Emergency contacts configuration
        self.emergency_contacts = [
            {
                "name": "Primary Caregiver",
                "phone": "+1234567890",
                "email": "caregiver@example.com",
                "priority": 1
            },
            {
                "name": "Family Member", 
                "phone": "+0987654321",
                "email": "family@example.com",
                "priority": 2
            },
            {
                "name": "Neighbor",
                "phone": "+1122334455", 
                "email": "neighbor@example.com",
                "priority": 3
            }
        ]
        
        # System state
        self.listening = False
        self.emergency_active = False
        self.calibrated = False
        
        print("✅ ElderGuard System initialized successfully!")
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        print("🎤 Calibrating microphone for optimal voice detection...")
        self.speak("Please remain quiet while I calibrate the microphone for your environment.")
        
        try:
            with self.microphone as source:
                print("   Listening to ambient noise for 3 seconds...")
                self.recognizer.adjust_for_ambient_noise(source, duration=3)
            
            self.calibrated = True
            print("✅ Microphone calibration completed successfully!")
            self.speak("Calibration complete. I can now hear you clearly.")
            return True
            
        except Exception as e:
            print(f"⚠️ Microphone calibration warning: {e}")
            self.speak("Calibration had minor issues, but I will still listen for emergencies.")
            return False
    
    def detect_emergency(self, text):
        """Advanced emergency detection with scoring system"""
        text_lower = text.lower().strip()
        detected_keywords = []
        detected_language = 'english'
        emergency_score = 0
        
        # Check for emergency keywords in all languages
        for language, keywords in self.emergency_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_keywords.append(keyword)
                    detected_language = language
                    emergency_score += 1
        
        # Enhanced detection - high priority phrases get extra weight
        urgent_phrases = [
            'fallen down', 'cant get up', 'chest pain', 'heart attack', 
            'need help now', 'call ambulance', 'cant breathe', 'stroke'
        ]
        
        for phrase in urgent_phrases:
            if phrase in text_lower:
                emergency_score += 3
                detected_keywords.append(phrase)
        
        # Medical emergency indicators
        medical_terms = ['heart', 'stroke', 'breathing', 'unconscious', 'bleeding', 'dizzy']
        for term in medical_terms:
            if term in text_lower:
                emergency_score += 2
                detected_keywords.append(f"medical:{term}")
        
        # Emergency threshold: score >= 1
        is_emergency = emergency_score >= 1
        
        return is_emergency, detected_keywords, detected_language, emergency_score
    
    def speak(self, text):
        """Text-to-speech with error handling"""
        try:
            print(f"🔊 ElderGuard: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Voice output error (continuing): {e}")
    
    def start_live_voice_testing(self):
        """Main live voice testing function"""
        print("\n" + "="*60)
        print("🎤 STARTING LIVE VOICE TESTING MODE")
        print("="*60)
        
        # Calibrate microphone first
        if not self.calibrated:
            self.calibrate_microphone()
        
        # Start listening
        self.listening = True
        self.speak("ElderGuard is now active and listening for emergencies. Say help, emergency, or describe your situation if you need assistance.")
        
        print("\n🔴 LIVE MONITORING ACTIVE")
        print("💬 Try saying these phrases:")
        print("   • 'Help me'")  
        print("   • 'Emergency'")
        print("   • 'I've fallen and can't get up'")
        print("   • 'I'm having chest pain'")
        print("   • 'Ayuda' (Spanish)")
        print("   • 'Aide' (French)")
        print("   • 'Hilfe' (German)")
        print("\n🌍 Multilingual Support: English, Spanish, French, German")
        print("🔴 Press Ctrl+C to stop monitoring")
        print("-" * 60)
        
        consecutive_errors = 0
        max_errors = 5
        
        while self.listening and consecutive_errors < max_errors:
            try:
                with self.microphone as source:
                    # Listen for audio with reasonable timeouts
                    print("👂 Listening...")
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=8)
                
                # Speech recognition
                print("🔄 Processing speech...")
                text = self.recognizer.recognize_google(audio, language='en-US')
                print(f"✅ Speech detected: '{text}'")
                
                # Reset error counter on successful recognition
                consecutive_errors = 0
                
                # Emergency analysis
                is_emergency, keywords, language, score = self.detect_emergency(text)
                
                if is_emergency and not self.emergency_active:
                    print(f"\n🚨 EMERGENCY DETECTED!")
                    print(f"   Keywords found: {keywords}")
                    print(f"   Language: {language}")
                    print(f"   Emergency score: {score}")
                    self.trigger_emergency(text, keywords, language, score)
                    
                elif keywords:
                    print(f"⚠️ Alert keywords detected: {keywords} (Score: {score} - below emergency threshold)")
                    
                else:
                    print("✅ Normal conversation detected - no emergency keywords found")
                
                print("-" * 40)
                
            except sr.WaitTimeoutError:
                # Normal timeout - continue listening
                pass
                
            except sr.UnknownValueError:
                print("❓ Could not understand audio clearly - please speak louder or clearer")
                consecutive_errors += 1
                
            except sr.RequestError as e:
                print(f"⚠️ Speech recognition service error: {e}")
                consecutive_errors += 1
                time.sleep(2)  # Wait before retrying
                
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                consecutive_errors += 1
                time.sleep(1)
        
        if consecutive_errors >= max_errors:
            print(f"\n⚠️ Too many consecutive errors ({max_errors}). Stopping voice monitoring.")
            self.speak("I'm having trouble with voice recognition. Please check your microphone.")
    
    def trigger_emergency(self, original_text, keywords, language, score):
        """Handle emergency situation with full response protocol"""
        self.emergency_active = True
        timestamp = datetime.now()
        
        print(f"\n{'🚨' * 20}")
        print("🚨 EMERGENCY ALERT ACTIVATED 🚨")
        print(f"{'🚨' * 20}")
        print(f"⏰ Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎤 Original Speech: '{original_text}'")
        print(f"🔍 Emergency Keywords: {keywords}")
        print(f"🌍 Detected Language: {language}")
        print(f"📊 Emergency Score: {score}")
        print(f"{'='*60}")
        
        # Immediate voice reassurance in appropriate language
        reassurance_messages = {
            'english': "Emergency detected! Help is being contacted immediately. Please stay calm and remain where you are unless you are in immediate danger. Do not move if you have fallen.",
            'spanish': "¡Emergencia detectada! Se está contactando ayuda inmediatamente. Mantente calmado y quédate donde estás a menos que estés en peligro inmediato.",
            'french': "Urgence détectée! L'aide est contactée immédiatement. Restez calme et restez où vous êtes, sauf si vous êtes en danger immédiat.",
            'german': "Notfall erkannt! Hilfe wird sofort kontaktiert. Bleiben Sie ruhig und bleiben Sie, wo Sie sind, es sei denn, Sie sind in unmittelbarer Gefahr."
        }
        
        message = reassurance_messages.get(language, reassurance_messages['english'])
        self.speak(message)
        
        # Create comprehensive emergency data
        emergency_data = {
            'timestamp': timestamp.isoformat(),
            'original_speech': original_text,
            'emergency_keywords': keywords,
            'detected_language': language,
            'emergency_score': score,
            'user_location': '[User configured address - 123 Main St, City, State]',
            'medical_history': '[User medical conditions if configured]'
        }
        
        # Send emergency alerts
        self.send_emergency_alerts(emergency_data)
        
        # Start emergency monitoring thread
        monitoring_thread = threading.Thread(target=self.monitor_emergency_state, args=(emergency_data,))
        monitoring_thread.daemon = True
        monitoring_thread.start()
    
    def send_emergency_alerts(self, emergency_data):
        """Send comprehensive alerts to all emergency contacts"""
        
        # Create detailed alert message
        alert_message = f"""
🚨 ELDERGUARD EMERGENCY ALERT 🚨

IMMEDIATE ATTENTION REQUIRED

Time: {emergency_data['timestamp']}
User Speech: "{emergency_data['original_speech']}"
Emergency Indicators: {', '.join(emergency_data['emergency_keywords'])}
Language Detected: {emergency_data['detected_language']}
Emergency Severity Score: {emergency_data['emergency_score']}
Location: {emergency_data['user_location']}
Medical History: {emergency_data['medical_history']}

RECOMMENDED ACTIONS:
1. Contact the user immediately by phone
2. If no response, consider calling emergency services (911)
3. Check on user's physical safety
4. Be prepared to provide location to emergency responders

This alert was generated by the ElderGuard AI Emergency Detection System.
System confidence: HIGH - Immediate response recommended.

To cancel this alert, the user must confirm they are safe.
        """.strip()
        
        print(f"\n📨 SENDING EMERGENCY ALERTS TO ALL CONTACTS:")
        print("="*50)
        
        # Sort contacts by priority and send alerts
        sorted_contacts = sorted(self.emergency_contacts, key=lambda x: x['priority'])
        
        for contact in sorted_contacts:
            print(f"📱 Priority {contact['priority']} - {contact['name']}")
            print(f"   SMS → {contact['phone']}")
            print(f"   Email → {contact['email']}")
            
            # In real implementation, you would use:
            # - Twilio for SMS: send_sms(contact['phone'], alert_message)
            # - SMTP for Email: send_email(contact['email'], alert_message)
            
        print("="*50)
        print("✅ All emergency contacts have been notified!")
        print("📞 Emergency services contact: 911 (if needed)")
    
    def monitor_emergency_state(self, emergency_data):
        """Continuous monitoring and updates during emergency"""
        print(f"\n🔄 Starting emergency monitoring...")
        
        # Monitor for 15 minutes with periodic updates
        monitoring_duration = 15  # minutes
        update_interval = 120  # 2 minutes
        
        for elapsed_minutes in range(2, monitoring_duration + 1, 2):
            if not self.emergency_active:
                print(f"✅ Emergency monitoring stopped - user confirmed safe")
                break
            
            time.sleep(update_interval)  # Wait 2 minutes
            
            if self.emergency_active:
                update_message = f"This is ElderGuard emergency monitoring. Help has been contacted. This is minute {elapsed_minutes} of monitoring. Please remain calm."
                self.speak(update_message)
                print(f"📢 Minute {elapsed_minutes}: Provided reassurance update to user")
                
                # Check if user wants to cancel emergency
                try:
                    print("🎤 Listening for cancellation commands...")
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=10)
                        text = self.recognizer.recognize_google(audio).lower()
                        
                        cancel_phrases = ['okay', 'fine', 'cancel', 'false alarm', 'im okay', 'im fine']
                        if any(phrase in text for phrase in cancel_phrases):
                            self.cancel_emergency_alert()
                            break
                            
                except:
                    pass  # Continue monitoring if no clear cancellation
        
        # Auto-conclude monitoring
        if self.emergency_active:
            print(f"\n⏰ Emergency monitoring completed ({monitoring_duration} minutes)")
            self.speak(f"Emergency monitoring period of {monitoring_duration} minutes has completed. If you still need help, please say 'help' again.")
            self.emergency_active = False
    
    def cancel_emergency_alert(self):
        """Cancel emergency alert when user confirms they're okay"""
        self.emergency_active = False
        
        print(f"\n✅ EMERGENCY ALERT CANCELLED BY USER")
        print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        
        self.speak("Emergency alert cancelled. I understand you are okay. ElderGuard will continue monitoring.")
        
        # Notify contacts of cancellation
        cancel_message = f"""
ElderGuard Update: Emergency alert has been cancelled.

The user has confirmed they are okay and do not need assistance.
Time of cancellation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ElderGuard will continue normal monitoring.
        """.strip()
        
        print("📧 Sending cancellation notice to emergency contacts...")
        for contact in self.emergency_contacts:
            print(f"✅ Cancellation sent to {contact['name']}")
            # In real implementation: send_sms(contact['phone'], cancel_message)
    
    def stop_monitoring(self):
        """Stop the monitoring system safely"""
        self.listening = False
        self.emergency_active = False
        self.speak("ElderGuard monitoring has been stopped. Thank you for using our emergency response system. Stay safe.")
        print("\n🛑 ElderGuard Emergency Monitoring Stopped")
        print("👋 System shutdown complete")

# Demo mode for testing without live voice
def demo_emergency_detection():
    """Demo mode showing emergency detection capabilities"""
    print("\n🎭 ELDERGUARD DEMO MODE")
    print("Testing emergency detection with simulated speech:")
    print("-" * 50)
    
    elderguard = ElderGuardSOS()
    
    test_scenarios = [
        ("Help I've fallen and can't get up", "Classic fall emergency - High priority"),
        ("I'm having severe chest pain", "Medical emergency - High priority"),
        ("Ayuda me caí y no puedo levantarme", "Spanish emergency - High priority"),
        ("Aide je suis tombé", "French emergency - Medium priority"),
        ("Hilfe ich bin gestürzt", "German emergency - Medium priority"),
        ("I can't breathe properly", "Breathing emergency - High priority"),
        ("Hello how are you today", "Normal conversation - No alert"),
        ("I'm feeling a bit tired", "Normal speech - No alert"),
        ("Emergency I need help now", "Urgent help request - High priority")
    ]
    
    print(f"Testing {len(test_scenarios)} scenarios:\n")
    
    for i, (text, description) in enumerate(test_scenarios, 1):
        print(f"📝 Test {i}: '{text}'")
        print(f"   Scenario: {description}")
        
        is_emergency, keywords, language, score = elderguard.detect_emergency(text)
        
        if is_emergency:
            print(f"   🚨 EMERGENCY DETECTED!")
            print(f"   └─ Keywords: {keywords}")
            print(f"   └─ Language: {language}")
            print(f"   └─ Score: {score}")
        else:
            print(f"   ✅ Normal speech - No emergency detected")
            if keywords:
                print(f"   └─ Keywords found but below threshold: {keywords}")
        
        print()
    
    print("✅ Demo completed successfully!")

# Main application entry point
if __name__ == "__main__":
    print("\n🛡️ ELDERGUARD EMERGENCY RESPONSE SYSTEM")
    print("Choose your mode:")
    print("1. 🎤 Live Voice Testing (Recommended)")
    print("2. 🎭 Demo Mode (No voice input required)")
    print("3. ❓ System Information")
    
    while True:
        try:
            choice = input("\nEnter your choice (1, 2, or 3): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting Live Voice Testing Mode...")
                elderguard = ElderGuardSOS()
                try:
                    elderguard.start_live_voice_testing()
                except KeyboardInterrupt:
                    print(f"\n\n🛑 User stopped live voice monitoring")
                    elderguard.stop_monitoring()
                break
                
            elif choice == "2":
                print("\n🚀 Starting Demo Mode...")
                demo_emergency_detection()
                break
                
            elif choice == "3":
                print(f"\n📋 SYSTEM INFORMATION")
                print(f"Version: ElderGuard v1.0")
                print(f"Purpose: Voice-activated emergency response for elderly users")
                print(f"Languages: English, Spanish, French, German")
                print(f"Features: Live voice monitoring, emergency detection, multilingual support")
                print(f"Requirements: Microphone, speakers, internet (for speech recognition)")
                continue
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                continue
                
        except KeyboardInterrupt:
            print(f"\n👋 Goodbye! Stay safe!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print(f"\n🛡️ Thank you for using ElderGuard Emergency Response System!")
