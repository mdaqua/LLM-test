# provider.py
import random

class ProviderRouter:
    def __init__(self, config):
        self.providers = config["providers"]
        
    def get_provider(self):
        """随机选择可用供应商"""
        return random.choice(list(self.providers.keys()))
    
    def get_provider_config(self, name):
        """获取指定供应商配置"""
        return self.providers.get(name, {})