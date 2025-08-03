#!/usr/bin/env python3
"""
Test Script for Voice SOS System
Tests both text analysis and basic functionality without requiring microphone
"""

import sys
import time
from typing import Dict, List

def test_imports():
    """Test if all required imports work"""
    print("🔍 Testing imports...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        
        import transformers
        print(f"✅ Transformers {transformers.__version__}")
        
        import speech_recognition as sr
        print("✅ SpeechRecognition")
        
        import pyttsx3
        print("✅ pyttsx3 (TTS)")
        
        try:
            import pyaudio
            print("✅ PyAudio")
        except ImportError:
            print("⚠️ PyAudio not available (needed for live microphone)")
        
        print("✅ All core imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_text_analysis():
    """Test the core SOS detection without microphone"""
    print("\n🧪 Testing Text Analysis (No Microphone Needed)")
    print("=" * 50)
    
    # Import the minimalistic SOS detector
    try:
        from minimalistic_voice_sos import MinimalisticSOSDetector
        detector = MinimalisticSOSDetector()
        print("✅ Minimalistic SOS Detector initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        return False
    
    # Test cases
    test_cases = [
        # Emergency cases
        {"text": "help me please", "should_detect": True, "lang": "en-US"},
        {"text": "मदद करो", "should_detect": True, "lang": "hi-IN"},
        {"text": "সাহায্য চাই", "should_detect": True, "lang": "bn-IN"},
        {"text": "emergency assistance needed", "should_detect": True, "lang": "en-US"},
        
        # Non-emergency cases
        {"text": "hello how are you", "should_detect": False, "lang": "en-US"},
        {"text": "what's the weather today", "should_detect": False, "lang": "en-US"},
        {"text": "good morning", "should_detect": False, "lang": "en-US"},
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: '{test_case['text']}'")
        print(f"   Expected: {'EMERGENCY' if test_case['should_detect'] else 'NORMAL'}")
        
        try:
            # Test keyword detection
            result_dict = detector.analyze_text(test_case['text'])
            
            if result_dict['is_emergency']:
                print(f"   ✅ Emergency detected via {result_dict['method']}")
                result = "EMERGENCY"
            else:
                print("   ✅ No emergency detected")
                result = "NORMAL"
            
            # Check if result matches expectation
            expected = "EMERGENCY" if test_case['should_detect'] else "NORMAL"
            status = "✅ PASS" if result == expected else "❌ FAIL"
            print(f"   Result: {result} - {status}")
            
            results.append({
                "test": test_case['text'],
                "expected": expected,
                "actual": result,
                "passed": result == expected
            })
            
        except Exception as e:
            print(f"   ❌ Error during testing: {e}")
            results.append({
                "test": test_case['text'],
                "expected": "EMERGENCY" if test_case['should_detect'] else "NORMAL",
                "actual": "ERROR",
                "passed": False
            })
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 30)
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    accuracy = (passed / total) * 100
    
    print(f"Passed: {passed}/{total}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    for result in results:
        status = "✅" if result['passed'] else "❌"
        print(f"{status} {result['test'][:30]}: {result['expected']} → {result['actual']}")
    
    return accuracy > 70  # Consider 70%+ as passing

def test_tts():
    """Test text-to-speech functionality"""
    print("\n🗣️ Testing Text-to-Speech")
    print("=" * 30)
    
    try:
        import pyttsx3
        
        tts = pyttsx3.init()
        tts.setProperty('rate', 150)
        tts.setProperty('volume', 0.9)
        
        test_messages = [
            "Help is on the way. Stay calm.",
            "सहायता आ रही है। शांत रहें।",
            "সাহায্য আসছে। শান্ত থাকুন।"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"🎵 Playing message {i}: {message}")
            tts.say(message)
            tts.runAndWait()
            time.sleep(1)
        
        print("✅ TTS test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

def test_microphone():
    """Test microphone availability (optional)"""
    print("\n🎤 Testing Microphone (Optional)")
    print("=" * 30)
    
    try:
        import speech_recognition as sr
        import pyaudio
        
        recognizer = sr.Recognizer()
        microphones = sr.Microphone.list_microphone_names()
        
        print(f"Found {len(microphones)} microphone(s):")
        for i, mic in enumerate(microphones[:3]):  # Show first 3
            print(f"  {i+1}. {mic}")
        
        if microphones:
            print("✅ Microphone hardware detected")
            
            # Quick test
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ Microphone initialization successful")
                return True
            except Exception as e:
                print(f"⚠️ Microphone test failed: {e}")
                return False
        else:
            print("⚠️ No microphones found")
            return False
            
    except ImportError:
        print("⚠️ PyAudio not installed - microphone testing skipped")
        return False

def run_quick_demo():
    """Run a quick interactive demo"""
    print("\n🎮 Quick Interactive Demo")
    print("=" * 30)
    print("Type emergency phrases to test detection:")
    print("Examples: 'help me', 'मदद करो', 'সাহায্য চাই'")
    print("Type 'quit' to exit")
    
    try:
        from minimalistic_voice_sos import MinimalisticSOSDetector
        detector = MinimalisticSOSDetector()
        
        while True:
            user_input = input("\n📝 Enter text to analyze: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            print(f"🔍 Analyzing: '{user_input}'")
            
            # Use the analyze_text method from minimalistic detector
            result = detector.analyze_text(user_input)
            
            if result['is_emergency']:
                print(f"🚨 EMERGENCY - Detected via {result['method']}")
                print(f"🗣️ Response: {result['response']}")
            else:
                print("✅ Normal conversation detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def main():
    """Main testing function"""
    print("🧪 VOICE SOS SYSTEM TESTING SUITE")
    print("=" * 60)
    print("Testing your implementation before GitHub submission...")
    print()
    
    # Run all tests
    test_results = {}
    
    # Test 1: Imports
    test_results['imports'] = test_imports()
    
    if not test_results['imports']:
        print("\n❌ Cannot proceed - fix import issues first")
        return
    
    # Test 2: Text Analysis
    test_results['text_analysis'] = test_text_analysis()
    
    # Test 3: TTS
    test_results['tts'] = test_tts()
    
    # Test 4: Microphone (optional)
    test_results['microphone'] = test_microphone()
    
    # Final Summary
    print("\n🎯 FINAL TEST RESULTS")
    print("=" * 40)
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    critical_tests = ['imports', 'text_analysis']
    critical_passed = all(test_results[test] for test in critical_tests)
    
    if critical_passed:
        print("\n🎉 READY FOR SUBMISSION!")
        print("Critical functionality is working.")
        
        # Ask if user wants interactive demo
        demo_choice = input("\nRun interactive demo? (y/n): ").strip().lower()
        if demo_choice == 'y':
            run_quick_demo()
    else:
        print("\n⚠️ NEEDS FIXES")
        print("Fix critical issues before submitting.")
    
    print("\n" + "=" * 60)
    print("Testing complete!")

if __name__ == "__main__":
    main()
