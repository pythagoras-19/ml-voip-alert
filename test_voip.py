#!/usr/bin/env python3
"""
Test script for VoIP functionality
"""
import os
import sys
from dotenv import load_dotenv

# Add app directory to path
sys.path.append('app')

from app.notifier import VoIPNotifier
from app.schemas import AlertData, Factor

def test_voip_configuration():
    """Test VoIP configuration and connection"""
    print("🔧 Testing VoIP Configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    required_vars = ['ASTERISK_HOST', 'ASTERISK_USER', 'ASTERISK_PASS', 'ALERT_CALL_NUMBER']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set these in your .env file")
        return False
    
    print("✅ All required environment variables are set")
    
    # Test notifier initialization
    notifier = VoIPNotifier()
    
    if notifier.ami_available:
        print("✅ AMI configuration is complete")
    else:
        print("⚠️  AMI configuration incomplete - will use simulation mode")
    
    return True

def test_voip_alert():
    """Test sending a VoIP alert"""
    print("\n📞 Testing VoIP Alert...")
    
    # Create test alert data
    test_alert = AlertData(
        alert_id="test_alert_12345678",
        patient_token="test_patient_123",
        risk=0.85,
        top_factors=[
            Factor(feature="age", impact=0.15),
            Factor(feature="cp", impact=0.12),
            Factor(feature="oldpeak", impact=0.10)
        ],
        timestamp="2024-01-01T12:00:00"
    )
    
    # Test notifier
    notifier = VoIPNotifier()
    
    print(f"📋 Alert ID: {test_alert.alert_id}")
    print(f"📋 Patient Token: {test_alert.patient_token}")
    print(f"📋 Risk Score: {test_alert.risk:.1%}")
    print(f"📋 AMI Available: {notifier.ami_available}")
    
    if notifier.ami_available:
        print("🚀 Attempting to send VoIP alert...")
        success = notifier.notify_voice(test_alert)
        
        if success:
            print("✅ VoIP alert sent successfully!")
        else:
            print("❌ Failed to send VoIP alert")
    else:
        print("📱 Simulating VoIP alert (AMI not configured)")
        success = notifier.notify_voice(test_alert)
        print(f"✅ Simulation result: {success}")

def main():
    """Main test function"""
    print("🏥 ML VoIP Alert System - VoIP Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_voip_configuration()
    
    if config_ok:
        # Test alert
        test_voip_alert()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    
    if not config_ok:
        print("\n💡 To enable real VoIP alerts:")
        print("1. Set up Asterisk server")
        print("2. Configure AMI in manager.conf")
        print("3. Set environment variables in .env file")
        print("4. See VOIP_SETUP.md for detailed instructions")

if __name__ == "__main__":
    main()
