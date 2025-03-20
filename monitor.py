# monitor.py
from prometheus_client import Counter, Histogram

REQUEST_COUNTER = Counter(
    'api_requests_total',
    'Total API requests',
    ['provider', 'status']
)

RESPONSE_TIME = Histogram(
    'api_response_seconds',
    'API response time',
    ['provider']
)