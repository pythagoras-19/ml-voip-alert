import os
import socket
import logging
from typing import Optional
from .schemas import AlertData

logger = logging.getLogger(__name__)


class VoIPNotifier:
    def __init__(self):
        self.asterisk_host = os.getenv('ASTERISK_HOST')
        self.asterisk_port = int(os.getenv('ASTERISK_PORT', '5038'))
        self.asterisk_user = os.getenv('ASTERISK_USER')
        self.asterisk_pass = os.getenv('ASTERISK_PASS')
        self.alert_number = os.getenv('ALERT_CALL_NUMBER')
        
        # Check if all required config is present
        self.ami_available = all([
            self.asterisk_host,
            self.asterisk_user,
            self.asterisk_pass,
            self.alert_number
        ])
        
        if not self.ami_available:
            logger.warning("Asterisk AMI configuration incomplete, voice alerts will be simulated")

    def notify_voice(self, alert: AlertData) -> bool:
        """
        Send voice alert via Asterisk AMI or simulator.
        
        Args:
            alert: Alert data containing risk information
            
        Returns:
            True if alert was sent successfully, False otherwise
        """
        if not self.ami_available:
            return self._simulate_voice_alert(alert)
        
        try:
            # Create short ID for the alert
            short_id = alert.alert_id[-6:]  # Last 6 characters
            
            # Create TTS message (PHI-free)
            message = f"High-risk cardiac score for case {short_id}. Check your secure portal."
            
            # Connect to Asterisk AMI
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10 second timeout
            
            try:
                sock.connect((self.asterisk_host, self.asterisk_port))
                
                # Read initial response
                response = self._read_ami_response(sock)
                if not response.startswith('Asterisk'):
                    raise Exception("Invalid AMI response")
                
                # Login to AMI
                login_cmd = f"Action: Login\r\nUsername: {self.asterisk_user}\r\nSecret: {self.asterisk_pass}\r\n\r\n"
                sock.send(login_cmd.encode())
                
                response = self._read_ami_response(sock)
                if 'Success' not in response:
                    raise Exception("AMI login failed")
                
                # Originate call
                originate_cmd = (
                    f"Action: Originate\r\n"
                    f"Channel: SIP/{self.alert_number}\r\n"
                    f"Application: Playback\r\n"
                    f"Data: {message}\r\n"
                    f"Async: true\r\n\r\n"
                )
                sock.send(originate_cmd.encode())
                
                response = self._read_ami_response(sock)
                if 'Success' in response:
                    logger.info(f"Voice alert sent successfully for case {alert.alert_id}")
                    return True
                else:
                    logger.error(f"AMI Originate failed: {response}")
                    return False
                    
            finally:
                sock.close()
                
        except Exception as e:
            logger.error(f"Voice alert failed: {e}")
            return False

    def _read_ami_response(self, sock: socket.socket) -> str:
        """Read AMI response from socket"""
        response = b""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            response += data
            if b"\r\n\r\n" in response:
                break
        return response.decode('utf-8', errors='ignore')
    
    def _simulate_voice_alert(self, alert: AlertData) -> bool:
        """Simulate voice alert using system TTS"""
        try:
            import subprocess
            import platform
            
            # Create short ID for the alert
            short_id = alert.alert_id[-6:]  # Last 6 characters
            
            # Create TTS message (PHI-free)
            message = f"High-risk cardiac score for case {short_id}. Check your secure portal."
            
            logger.info(f"📞 SIMULATED VOIP CALL")
            logger.info(f"   📱 To: {self.alert_number or 'Unknown'}")
            logger.info(f"   💬 Message: {message}")
            
            # Use system TTS if available
            if platform.system() == "Darwin":  # macOS
                try:
                    subprocess.run([
                        "say", 
                        "-v", "Alex",
                        "-r", "150",
                        message
                    ], timeout=10, check=True)
                    logger.info("   ✅ Voice message played successfully")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    logger.info("   📢 Text-to-speech not available")
            else:
                logger.info("   📢 Text-to-speech not available on this system")
            
            return True
            
        except Exception as e:
            logger.error(f"Voice simulation failed: {e}")
            return False


# Global notifier instance
notifier = VoIPNotifier()
