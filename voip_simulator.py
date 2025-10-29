#!/usr/bin/env python3
"""
Simple VoIP Simulator for Mac M1
Simulates VoIP calls without requiring Asterisk
"""
import os
import time
import subprocess
import platform
from typing import Optional

class VoIPSimulator:
    def __init__(self):
        self.system = platform.system()
        self.voice_enabled = self._check_voice_capability()
    
    def _check_voice_capability(self) -> bool:
        """Check if system can do text-to-speech"""
        if self.system == "Darwin":  # macOS
            try:
                # Just check if say command exists
                subprocess.run(["which", "say"], capture_output=True, check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
        return False
    
    def make_call(self, phone_number: str, message: str) -> bool:
        """Simulate making a VoIP call"""
        print(f"📞 SIMULATED VOIP CALL")
        print(f"   📱 To: {phone_number}")
        print(f"   💬 Message: {message}")
        print(f"   ⏱️  Duration: 3 seconds")
        
        if self.voice_enabled:
            try:
                # Use macOS 'say' command for TTS
                subprocess.run([
                    "say", 
                    "-v", "Alex",  # Use Alex voice
                    "-r", "150",   # Speed
                    message
                ], timeout=10)
                print("   ✅ Voice message played successfully")
            except subprocess.TimeoutExpired:
                print("   ⚠️  Voice message timed out")
            except Exception as e:
                print(f"   ❌ Voice error: {e}")
        else:
            print("   📢 Text-to-speech not available on this system")
        
        # Simulate call duration
        time.sleep(2)
        print("   📞 Call ended")
        return True
    
    def test_connection(self) -> bool:
        """Test VoIP simulator"""
        print("🔧 Testing VoIP Simulator...")
        print(f"   System: {self.system}")
        print(f"   Voice enabled: {self.voice_enabled}")
        return True

def main():
    """Test the VoIP simulator"""
    print("🏥 ML VoIP Alert System - VoIP Simulator")
    print("=" * 50)
    
    simulator = VoIPSimulator()
    
    # Test connection
    simulator.test_connection()
    
    # Test call
    print("\n📞 Testing simulated call...")
    simulator.make_call(
        phone_number="555-123-4567",
        message="High-risk cardiac score for case ABC123. Check your secure portal."
    )
    
    print("\n✅ VoIP Simulator test completed!")

if __name__ == "__main__":
    main()
