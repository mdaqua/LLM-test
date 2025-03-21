import json
from config import load_config
from provider import ProviderRouter
from api import API
from cache import APICache
from request_orchestrator import RequestOrchestrator

def add_case_identifier(input_file, output_file):
    """为文件的每条案件前添加标识符"""
    with open(input_file, 'r', encoding='utf-8') as f:
        # 读取原始内容并按换行分割，过滤空行
        cases = [line.strip() for line in f.read().split('\n') if line.strip()]

    # 添加案件标识
    processed = [f"[案件标识: {i+1}] {case}" for i, case in enumerate(cases)]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(processed))

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
        case_id = answer_data.get("case_id", "")
        classification = answer_data.get("classification", "")
        keywords = answer_data.get("keywords", [])
        
        return case_id, classification, keywords
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error extracting data from response: {e}")
        return "", []

def write_results(results, file_path):
    """将结果写入文件"""
    with open(file_path, "w", encoding="utf-8") as file:
        for response in results:
            case_id, classification, keywords = extract_info(response)
            # 输出格式化
            file.write(f"Case ID: {case_id}\n")
            file.write(f"Classification: {classification}\n")
            file.write(f"Keywords: {', '.join(keywords)}\n")
            file.write("\n")  # 空行分隔

def main():
    # 初始化组件
    config = load_config()
    router = ProviderRouter(config)
    api = API(router)
    cache = APICache(config["cache"]["ttl"])
    orchestrator = RequestOrchestrator(api, cache)

    # 从文件读取消息
    add_case_identifier("test/input_messages.txt", "test/input_messages_with_id.txt")
    input_file = "test/input_messages_with_id.txt"  # 输入文件路径
    requests = read_messages(input_file)

    # 执行并发请求
    responses = orchestrator.parallel_requests(requests)

    # 将结果写入文件
    output_file = "test/output_results.txt"  # 输出文件路径
    write_results(responses, output_file)

    print(f"结果已保存至 {output_file}")

if __name__ == "__main__":
    main()