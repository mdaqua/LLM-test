# cache.py
import time
import hashlib
from threading import Lock

class APICache:
    def __init__(self, ttl=300):
        self.ttl = ttl
        self._cache = {}
        self._lock = Lock()
    
    def generate_request_hash(self, messages):
        """生成请求哈希"""
        return hashlib.md5(str(messages).encode()).hexdigest()
    
    def get_cached_response(self, request_hash: str):
        """获取缓存响应，支持TTL控制"""
        with self._lock:
            entry = self._cache.get(request_hash)
            if entry and time.time() < entry['expiry']:
                return entry['response']
            elif entry:
                # 缓存过期后删除
                del self._cache[request_hash]
        return None
    
    def set_cache(self, request_hash: str, response):
        """设置缓存响应"""
        with self._lock:
            self._cache[request_hash] = {
                'response': response,
                'expiry': time.time() + self.ttl
            }
