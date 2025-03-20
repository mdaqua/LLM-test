# error_handler.py

class APIError(Exception):
    """基础异常类"""
    
class ConfigurationError(APIError):
    """配置错误"""

class APIRequestError(APIError):
    """API请求失败"""
    def __init__(self, provider, message):
        self.provider = provider
        super().__init__(f"[{provider}] {message}")

class RateLimitError(APIRequestError):
    """速率限制异常"""
    def __init__(self, provider):
        super().__init__(provider, "Rate limit exceeded")