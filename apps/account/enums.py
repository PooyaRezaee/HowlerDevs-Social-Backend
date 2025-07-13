from enum import Enum
from .models import User

class CacheKeyPrefix(Enum):
    RESET_2FA = "reset_2fa"
    RESET_PASSWORD = "reset_password"
    RESET_EMAIL = "reset_email"
    LOGIN_2FA = "login_2fa"
    
    def key(self, suffix: str):
        return f"{self.value}:{suffix}"