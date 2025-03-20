# request_orchestrator.py
from concurrent.futures import ThreadPoolExecutor

class RequestOrchestrator:
    def __init__(self, api, cache):
        self.api = api
        self.cache = cache
        
    def parallel_requests(self, requests_list):
        """并发执行多个请求"""
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._process_request, req)
                for req in requests_list
            }
            return [future.result() for future in futures]
            
    def _process_request(self, messages):
        """带缓存的请求处理"""
        if request_hash := self.cache.generate_request_hash(messages):
            if cached := self.cache.get_cached_response(request_hash):
                return cached
                
        response = self.api.execute(messages)
        self.cache.set_cache(request_hash, response)
        return response