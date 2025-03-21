# config.py
from pathlib import Path
import json
import sys

# CONFIG_PATH = Path.home() / ".config/api_service/config.json"
CONFIG_PATH = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "providers": {
        "dify": {
            "base_url": "https://api.dify.ai/v1/chat-messages",
            "api_keys": ["app-"],
            "timeout": 15,
            "max_retries": 1
        }
    },
    "cache": {
        "enabled": True,
        "ttl": 300  # 秒
    }
}

def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print("请配置 config.json 文件")
        sys.exit(1)