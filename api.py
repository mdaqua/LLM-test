# api.py
import random
import time
import requests
from error_handler import APIRequestError, RateLimitError
from monitor import REQUEST_COUNTER, RESPONSE_TIME

class API:
    def __init__(self, router):
        self.router = router

    def execute(self, messages):
        """执行API请求，集成重试机制与监控"""
        provider_name = self.router.get_provider()
        config = self.router.get_provider_config(provider_name)
        max_retries = config.get("max_retries", 1)
        attempt = 0

        while attempt < max_retries:
            attempt += 1
            start_time = time.time()
            try:
                # response = requests.post(
                #     f"{config['base_url']}/chat/completions",
                #     headers={"Authorization": f"Bearer {self._get_api_key(config)}"},
                #     json={"messages": messages},
                #     timeout=config["timeout"]
                # )

                response = requests.post(
                    f"{config['base_url']}/chat-messages",
                    headers={"Authorization": f"Bearer {self._get_api_key(config)}"},
                    json={
                        "inputs": {},
                        "query": messages,
                        "response_mode": "blocking",
                        "conversation_id": "",
                        "user": "1",
                    },
                )
                response.raise_for_status()
                elapsed = time.time() - start_time
                RESPONSE_TIME.labels(provider=provider_name).observe(elapsed)
                REQUEST_COUNTER.labels(provider=provider_name, status="success").inc()
                return response.json()
            except requests.HTTPError as e:
                elapsed = time.time() - start_time
                RESPONSE_TIME.labels(provider=provider_name).observe(elapsed)
                REQUEST_COUNTER.labels(provider=provider_name, status="failed").inc()
                if e.response.status_code == 429:
                    raise RateLimitError(provider_name)
                if attempt >= max_retries:
                    raise APIRequestError(provider_name, str(e))
            except requests.RequestException as e:
                elapsed = time.time() - start_time
                RESPONSE_TIME.labels(provider=provider_name).observe(elapsed)
                REQUEST_COUNTER.labels(provider=provider_name, status="failed").inc()
                if attempt >= max_retries:
                    raise APIRequestError(provider_name, str(e))
                # 重试前等待
                time.sleep(1)
            
    def _get_api_key(self, config):
        """轮询API密钥"""
        return random.choice(config["api_keys"])
    
    def _get_params(self, config):
        """获取请求参数"""
        return {
            "timeout": config["timeout"]
        }
