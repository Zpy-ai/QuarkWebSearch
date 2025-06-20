import dashscope

dashscope.api_key = "sk-139a40229c0e4bd58191a7a2f8c9c8f3"

import dashscope
from http import HTTPStatus
import json

# 检查操作状态的函数
def check_status(component, operation):
    return component.status_code == HTTPStatus.OK

# 1. 创建Web搜索助手
search_assistant = dashscope.Assistants.create(
    model='qwen-max',
    name='Web Search Pro',
    description='专注于网络信息检索的AI助手',
    instructions='''使用夸克搜索工具获取互联网上的最新信息、百科知识、新闻等各类内容，
    并以清晰、简洁的方式总结和呈现搜索结果。''',
    tools=[
        {'type': 'quark_search', 'description': '用于查找互联网上的最新信息、百科知识、新闻等各类内容。'}
    ]
)

if not check_status(search_assistant, "助手创建"):
    exit()

# 2. 创建一个新线程
thread = dashscope.Threads.create()

if not check_status(thread, "线程创建"):
    exit()

# 3. 向线程发送消息（用户查询）
user_query = "2025年人工智能领域有哪些最新突破？"
message = dashscope.Messages.create(thread.id, content=user_query)

if not check_status(message, "消息创建"):
    exit()

# 4. 在线程上运行助手
run = dashscope.Runs.create(thread.id, assistant_id=search_assistant.id)

if not check_status(run, "运行创建"):
    exit()

# 5. 等待运行完成
print("等待助手处理请求...")
run = dashscope.Runs.wait(run.id, thread_id=thread.id)

if check_status(run, "运行完成"):
    print(f"运行完成，状态：{run.status}")
else:
    exit()

# 6. 检索并显示助手的响应
messages = dashscope.Messages.list(thread.id)

if check_status(messages, "消息检索"):
    if messages.data:
        # 显示最后一条消息的内容（助手的响应）
        last_message = messages.data[0]
        print("\n助手的回应：")
        print(json.dumps(last_message, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4))