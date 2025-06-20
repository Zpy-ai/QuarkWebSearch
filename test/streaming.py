import dashscope
from http import HTTPStatus
import json
import sys

dashscope.api_key = "sk-139a40229c0e4bd58191a7a2f8c9c8f3"

# 检查操作状态的函数
def check_status(component, operation):
    if component.status_code == HTTPStatus.OK:
        print(f"{operation} 成功。")
        return True
    else:
        print(f"{operation} 失败。状态码：{component.status_code}，错误码：{component.status_code}，错误信息：{component.status_code}")
        sys.exit(component.status_code)

# 1. 创建Web搜索助手
def create_search_assistant():
    return dashscope.Assistants.create(
        model='qwen-max',
        name='Web Search Pro',
        description='专注于网络信息检索的AI助手',
        instructions='''使用夸克搜索工具获取互联网上的最新信息、百科知识、新闻等各类内容，
        并以清晰、简洁的方式总结和呈现搜索结果。''',
        tools=[
            {'type': 'quark_search', 'description': '用于查找互联网上的最新信息、百科知识、新闻等各类内容。'}
        ]
    )

'''if not check_status(search_assistant, "助手创建"):
    exit()'''


if __name__ == '__main__':
    # 创建搜索助手
    search_assistant = create_search_assistant()
    check_status(search_assistant, "助手创建")

    # 用户查询内容
    user_query = "2025年人工智能领域有哪些最新突破？"
    
    # 创建一个带有初始消息的新线程
    thread = dashscope.Threads.create(
        messages=[{
            'role': 'user',
            'content': user_query
        }]
    )
    check_status(thread, "线程创建")

    # 创建流式输出的运行
    run_iterator = dashscope.Runs.create(
        thread.id,
        assistant_id=search_assistant.id,
        stream=True
    )

    # 迭代事件和消息
    print("处理请求中...")
    for event, msg in run_iterator:
        print(event)
        print(msg)

    # 检索并显示完整消息历史
    messages = dashscope.Messages.list(thread.id)
    check_status(messages, "消息检索")

    print("\n完整搜索结果:")
    print(json.dumps(messages, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4))