# -*- coding: utf-8 -*-
import os
import json
import requests
from typing import Dict, Any, List, Optional

class ConfigHandler:
    """配置文件处理类"""
    _CONFIG_PATH = "config.json"
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """从本地文件加载配置"""
        try:
            with open(cls._CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 基础校验
            if not config.get("api_key"):
                raise ValueError("API key缺失")
            return config
        except FileNotFoundError:
            raise Exception(f"配置文件 {cls._CONFIG_PATH} 未找到")
        except json.JSONDecodeError:
            raise Exception("配置文件格式错误")

class EnhancedDeepSeekAPI:
    """增强版API处理器"""
    def __init__(self, api_key: str):
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.max_retries = 2  # 新增重试机制
    
    def call_with_context(self, context: List[Dict[str, str]], max_tokens: int = 2000) -> Optional[Dict]:
        """带流量控制和安全限制的API调用"""
        payload = {
            "model": "deepseek-chat",
            "messages": context,
            "temperature": 0.7,
            "max_tokens": max_tokens
        }
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,  # 自动处理序列化
                    timeout=15
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and attempt < self.max_retries:
                    print(f"触发限频，第{attempt+1}次重试...")
                    continue
                print(f"API错误: {str(e)}")
                return None
            except Exception as e:
                print(f"请求异常: {str(e)}")
                return None

class AdvancedConversationManager:
    """增强版对话管理器"""
    def __init__(self, scenario: str):
        self.history = []
        self.scenario = scenario
        self._init_system_prompt()
        self.max_context_length = 3000  # 基于token的上下文限制
        
    def _init_system_prompt(self):
        """初始化系统提示"""
        system_prompt = {
            "smart_home": "你是一个智能家居控制助手，需要解析设备操作指令并按JSON格式返回，包含device和action字段。",
            "community_service": "你是一个社区服务助手，需先确认问题类型，然后收集必要信息。",
            "security": "安防监控助手，需分析事件并生成包含时间、地点、类型的警报报告。"
        }.get(self.scenario, "通用助手")
        
        self.add_message("system", system_prompt, safe=True)
    
    def add_message(self, role: str, content: str, safe: bool = True) -> None:
        """安全添加消息（新增内容截断）"""
        if safe:
            content = self._truncate_content(content)
        self.history.append({"role": role, "content": content})
    
    def _truncate_content(self, text: str, max_len: int = 1000) -> str:
        """防止过长内容（安全处理）"""
        return text[:max_len] + "...[TRUNCATED]" if len(text) > max_len else text
    
    def get_optimized_context(self) -> List[Dict[str, str]]:
        """智能上下文管理（新增token估算）"""
        current_length = sum(len(msg["content"]) for msg in self.history) // 4  # 简易token估算
        
        if current_length <= self.max_context_length:
            return self.history.copy()
            
        # 逐步移除最早的非系统消息
        trimmed_history = [self.history[0]]  # 保留系统提示
        for msg in reversed(self.history[1:]):
            trimmed_history.insert(1, msg)
            current_length = sum(len(m["content"]) for m in trimmed_history) //4
            if current_length > self.max_context_length:
                trimmed_history.pop(1)
                break
                
        return trimmed_history
    
    def change_scenario(self, new_scenario: str) -> None:
        """动态切换场景（新增功能）"""
        if new_scenario != self.scenario:
            self.scenario = new_scenario
            old_history = self.history[1:]  # 保留之前的对话
            self.history = []
            self._init_system_prompt()
            self.history.extend(old_history)

# 使用示例
if __name__ == "__main__":
    try:
        # 从本地文件加载配置
        config = ConfigHandler.load_config()
        api_key = config["api_key"]
        
        # 初始化系统
        api = EnhancedDeepSeekAPI(api_key)
        conv_mgr = AdvancedConversationManager("smart_home")
        
        # 模拟多轮对话
        test_inputs = [
            "请关闭客厅的灯",
            "不，我指的是主卧的灯",
            "顺便把空调调到26度然后打开加湿器"
        ]
        
        for idx, user_input in enumerate(test_inputs, 1):
            print(f"\n—— 第 {idx} 轮交互 ——")
            
            # 安全添加用户输入
            conv_mgr.add_message("user", user_input)
            
            # 获取优化后的上下文
            context = conv_mgr.get_optimized_context()
            
            # 调用API
            response = api.call_with_context(context)
            
            if response:
                try:
                    content = response['choices'][0]['message']['content']
                    print(f"用户输入: {user_input}")
                    print(f"模型响应: {content}")
                    
                    # 解析并执行命令
                    if conv_mgr.scenario == "smart_home":
                        command = json.loads(content)
                        print(f"执行: {command['device']} → {command['action']}")
                        
                    # 添加助手响应
                    conv_mgr.add_message("assistant", content)
                    
                except json.JSONDecodeError:
                    print("响应解析失败，请检查模型输出格式")
                except KeyError:
                    print("响应结构异常")
                    
        print("\n最终上下文状态：")
        for msg in conv_mgr.get_optimized_context():
            print(f"[{msg['role'].upper()}] {msg['content'][:50]}...")
            
    except Exception as e:
        print(f"系统初始化失败: {str(e)}")