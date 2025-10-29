import os
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import redis
from .schemas import AlertData


class Storage:
    def __init__(self):
        self.redis_client = None
        self.memory_store = {}
        self.cooldowns = {}
        
        # Try to connect to Redis
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()  # Test connection
            except Exception as e:
                print(f"Redis connection failed, using in-memory storage: {e}")
                self.redis_client = None

    def in_cooldown(self, patient_token: str) -> bool:
        """Check if patient is in cooldown period"""
        cooldown_minutes = int(os.getenv('COOLDOWN_MINUTES', '30'))
        
        if self.redis_client:
            try:
                cooldown_key = f"cooldown:{patient_token}"
                last_alert = self.redis_client.get(cooldown_key)
                if last_alert:
                    last_alert_time = datetime.fromisoformat(last_alert.decode())
                    return datetime.now() - last_alert_time < timedelta(minutes=cooldown_minutes)
                return False
            except Exception as e:
                print(f"Redis cooldown check failed: {e}")
                return False
        else:
            # In-memory fallback
            if patient_token in self.cooldowns:
                last_alert_time = self.cooldowns[patient_token]
                return datetime.now() - last_alert_time < timedelta(minutes=cooldown_minutes)
            return False

    def set_cooldown(self, patient_token: str):
        """Set cooldown for patient"""
        now = datetime.now()
        
        if self.redis_client:
            try:
                cooldown_key = f"cooldown:{patient_token}"
                self.redis_client.set(cooldown_key, now.isoformat())
            except Exception as e:
                print(f"Redis cooldown set failed: {e}")
                self.cooldowns[patient_token] = now
        else:
            self.cooldowns[patient_token] = now

    def save_alert(self, alert: AlertData):
        """Save alert data"""
        if self.redis_client:
            try:
                alert_key = f"alert:{alert.alert_id}"
                self.redis_client.set(alert_key, alert.model_dump_json())
            except Exception as e:
                print(f"Redis alert save failed: {e}")
                self.memory_store[alert.alert_id] = alert
        else:
            self.memory_store[alert.alert_id] = alert

    def get_alert(self, alert_id: str) -> Optional[AlertData]:
        """Get alert by ID"""
        if self.redis_client:
            try:
                alert_key = f"alert:{alert_id}"
                alert_data = self.redis_client.get(alert_key)
                if alert_data:
                    return AlertData.model_validate_json(alert_data)
                return None
            except Exception as e:
                print(f"Redis alert get failed: {e}")
                return self.memory_store.get(alert_id)
        else:
            return self.memory_store.get(alert_id)


# Global storage instance
storage = Storage()
