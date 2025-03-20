# main.py
from config import load_config
from provider import ProviderRouter
from api import API
from cache import APICache
from request_orchestrator import RequestOrchestrator

# 初始化组件
config = load_config()
router = ProviderRouter(config)
api = API(router)
cache = APICache(config["cache"]["ttl"])
orchestrator = RequestOrchestrator(api, cache)

# 测试: 执行并发请求
# requests = [
#     [{"role": "user", "content": "你好"}],
#     [{"role": "user", "content": "天气如何"}]
# ]

# results = orchestrator.parallel_requests(requests)
# print(results)

requests = [
    [{"role": "user", "content": "周双妹来蓉旅游入住古可悦享酒店，因为酒店前台未经同意泄露给了周双妹友人房号，感到隐私权受到侵犯，双方产生纠纷。经调解，黎斌（酒店负责人）表示免除两天房费，将房间挪到一个僻静位置，并诚恳道歉，双方达成和解。"}]
]

results = orchestrator.parallel_requests(requests)
print(results)