# elderguard_web_demo.py - Beautiful Web Interface for ElderGuard
from flask import Flask, render_template, jsonify, request
import json
import threading
import time
from datetime import datetime
import speech_recognition as sr
import pyttsx3

app = Flask(__name__)

# Global variables for real-time updates
system_status = {
    'monitoring': False,
    'emergency_active': False,
    'last_heard': '',
    'emergency_count': 0,
    'uptime': 0,
    'language': 'english',
    'confidence': 0
}

class ElderGuardWebSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.listening = False
        
        # Emergency keywords
        self.keywords = {
            'english': ['help', 'emergency', 'fallen', 'pain', 'cant move'],
            'spanish': ['ayuda', 'emergencia', 'caído', 'dolor'],
            'french': ['aide', 'urgence', 'tombé', 'douleur'],
            'german': ['hilfe', 'notfall', 'gefallen', 'schmerz']
        }
    
    def detect_emergency(self, text):
        text_lower = text.lower()
        found_keywords = []
        language = 'english'
        
        for lang, words in self.keywords.items():
            for word in words:
                if word in text_lower:
                    found_keywords.append(word)
                    language = lang
        
        return len(found_keywords) > 0, found_keywords, language
    
    def start_background_monitoring(self):
        """Background voice monitoring with web status updates"""
        global system_status
        system_status['monitoring'] = True
        start_time = time.time()
        
        while self.listening:
            try:
                system_status['uptime'] = int(time.time() - start_time)
                
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                
                text = self.recognizer.recognize_google(audio)
                system_status['last_heard'] = text
                
                is_emergency, keywords, language = self.detect_emergency(text)
                system_status['language'] = language
                system_status['confidence'] = len(keywords) * 25  # Simple confidence calculation
                
                if is_emergency:
                    system_status['emergency_active'] = True
                    system_status['emergency_count'] += 1
                    system_status['last_emergency'] = {
                        'text': text,
                        'keywords': keywords,
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'language': language
                    }
                    
                    # Auto-reset emergency after 30 seconds for demo
                    threading.Timer(30.0, self.reset_emergency).start()
                
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                system_status['last_heard'] = '[Unclear audio]'
            except Exception as e:
                system_status['last_heard'] = f'[Error: {str(e)[:30]}]'
    
    def reset_emergency(self):
        global system_status
        system_status['emergency_active'] = False

# Initialize the system
elderguard = ElderGuardWebSystem()

# Flask Routes
@app.route('/')
def index():
    return render_template('elderguard_dashboard.html')

@app.route('/api/status')
def get_status():
    return jsonify(system_status)

@app.route('/api/start_monitoring')
def start_monitoring():
    if not elderguard.listening:
        elderguard.listening = True
        thread = threading.Thread(target=elderguard.start_background_monitoring)
        thread.daemon = True
        thread.start()
    return jsonify({'status': 'started'})

@app.route('/api/stop_monitoring')
def stop_monitoring():
    elderguard.listening = False
    system_status['monitoring'] = False
    return jsonify({'status': 'stopped'})

@app.route('/api/simulate_emergency')
def simulate_emergency():
    # Simulate emergency for demo
    system_status['emergency_active'] = True
    system_status['emergency_count'] += 1
    system_status['last_emergency'] = {
        'text': 'Help I\'ve fallen and can\'t get up',
        'keywords': ['help', 'fallen'],
        'time': datetime.now().strftime('%H:%M:%S'),
        'language': 'english'
    }
    # Auto-reset after 10 seconds for demo
    threading.Timer(10.0, elderguard.reset_emergency).start()
    return jsonify({'status': 'emergency_simulated'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
