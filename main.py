import json
from config import load_config
from provider import ProviderRouter
from api import API
from cache import APICache
from request_orchestrator import RequestOrchestrator

def read_messages(file_path):
    """从文件中读取消息，每行作为一条消息"""
    with open(file_path, "r", encoding="utf-8") as file:
        return [[{"role": "user", "content": line.strip()}] for line in file if line.strip()]

def extract_info(response):
    """从响应中提取信息"""
    try:
        # 提取 answer 部分
        answer = response["answer"]
        # 去掉 JSON 代码块的标记（如 ```json 和 ```）
        answer = answer.replace("```json\n", "").replace("\n```", "")
        # 解析 JSON
        answer_data = json.loads(answer)
        # 提取信息模块
        classification = answer_data.get("classification", "")
        keywords = answer_data.get("key_indicators", [])
        
        return classification, keywords
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error extracting data from response: {e}")
        return "", []

def write_results(results, file_path):
    """将结果写入文件"""
    with open(file_path, "w", encoding="utf-8") as file:
        for response in results:
            classification, keywords = extract_info(response)
            # 输出格式化
            file.write(f"Classification: {classification}\n")
            file.write(f"Key Indicators: {', '.join(keywords)}\n")
            file.write("\n")  # 空行分隔

def main():
    # 初始化组件
    config = load_config()
    router = ProviderRouter(config)
    api = API(router)
    cache = APICache(config["cache"]["ttl"])
    orchestrator = RequestOrchestrator(api, cache)

    # 从文件读取消息
    input_file = "test/input_messages.txt"  # 输入文件路径
    requests = read_messages(input_file)

    # 执行并发请求
    responses = orchestrator.parallel_requests(requests)

    # 将结果写入文件
    output_file = "test/output_results.txt"  # 输出文件路径
    write_results(responses, output_file)

    print(f"结果已保存至 {output_file}")

if __name__ == "__main__":
    main()