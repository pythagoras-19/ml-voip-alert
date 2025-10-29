# VoIP Setup Guide

## 🔧 **Asterisk AMI Configuration**

### **1. Install Asterisk**

**Option A: macOS with Homebrew**
```bash
brew install asterisk
sudo asterisk -vvv
```

**Option B: Docker (Recommended)**
```bash
docker run -d --name asterisk \
  -p 5060:5060/udp \
  -p 10000-20000:10000-20000/udp \
  -p 5038:5038 \
  andrius/asterisk:latest
```

### **2. Configure Asterisk Manager Interface**

Create `/etc/asterisk/manager.conf`:
```ini
[general]
enabled = yes
port = 5038
bindaddr = 0.0.0.0

[admin]
secret = your_password_here
permit = 0.0.0.0/0.0.0.0
read = system,call,log,verbose,agent,user,config,dtmf,reporting,cdr,dialplan
write = system,call,agent,user,config,command,reporting,originate
```

### **3. Environment Configuration**

Create a `.env` file in your project root:
```bash
# Model Configuration
MODEL_PATH=./models/heart_pipeline.joblib

# Risk Threshold (0.0 to 1.0)
RISK_THRESHOLD=0.80

# Alert Configuration
COOLDOWN_MINUTES=30

# Asterisk AMI Configuration (for VoIP alerts)
ASTERISK_HOST=localhost
ASTERISK_PORT=5038
ASTERISK_USER=admin
ASTERISK_PASS=your_password_here
ALERT_CALL_NUMBER=5551234567

# Redis Configuration (optional)
# REDIS_URL=redis://localhost:6379/0
```

### **4. Test VoIP Connection**

Test the AMI connection:
```bash
telnet localhost 5038
```

Then send:
```
Action: Login
Username: admin
Secret: your_password_here

Action: Ping

Action: Logoff
```

## 🚀 **Usage**

Once configured, the system will automatically:

1. **Detect high-risk patients** (risk > threshold)
2. **Generate alert ID** for tracking
3. **Make VoIP call** to the configured number
4. **Play TTS message**: "High-risk cardiac score for case [ID]. Check your secure portal."
5. **Set cooldown** to prevent spam

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **"AMI configuration incomplete"** - Check your `.env` file
2. **Connection refused** - Ensure Asterisk is running and AMI is enabled
3. **Authentication failed** - Verify username/password in manager.conf
4. **Call not connecting** - Check phone number format and SIP configuration

### **Debug Mode:**

Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## 📞 **Advanced Configuration**

### **Custom TTS Messages**

Modify `app/notifier.py` to customize the alert message:
```python
message = f"URGENT: High-risk cardiac patient {short_id}. Risk level: {alert.risk:.1%}. Immediate attention required."
```

### **Multiple Alert Numbers**

You can modify the notifier to call multiple numbers or use different numbers based on risk level.

### **SIP Trunk Configuration**

For production use, configure a SIP trunk to your phone provider in `/etc/asterisk/sip.conf`.

## 🛡️ **Security Notes**

- Use strong passwords for AMI
- Restrict AMI access to trusted IPs
- Consider using TLS for AMI connections
- Never expose Asterisk directly to the internet without proper security
