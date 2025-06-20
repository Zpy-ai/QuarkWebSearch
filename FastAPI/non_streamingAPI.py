import dashscope
from http import HTTPStatus
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
import json
from typing import Literal
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 环境变量传入
sk_key = os.environ.get("sk-key", "sk-proj-mimouse")

# 定义FastAPI应用
app = FastAPI(title="Web Search API", description="基于夸克搜索的AI助手API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# 请求模型
class SearchRequest(BaseModel):
    query: str
    tools: Literal ["quark_search"]


# 响应模型
class SearchResponse(BaseModel):
    response: str
    tools_used: str

dashscope.api_key = "sk-139a40229c0e4bd58191a7a2f8c9c8f3"

# 检查操作状态的函数
def check_status(component, operation):
    return component.status_code == HTTPStatus.OK

# 1. 创建Web搜索助手


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

@app.post("/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest ,
                          credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != sk_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization code",
        )
    # 创建搜索助手
    search_assistant = create_search_assistant()
    if not check_status(search_assistant, "助手创建"):
        exit()

    # 2. 创建一个新线程
    thread = dashscope.Threads.create()

    if not check_status(thread, "线程创建"):
        exit()

    # 3. 向线程发送消息（用户查询）
    user_query = request.query
    if not user_query:
        return {"response": "查询内容不能为空", "tools_used": ""}
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


        # 提取消息内容中的文本值
            assistant_text = ""
            if hasattr(last_message, 'content') and last_message.content:
                for content_item in last_message.content:
                    if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                        assistant_text += content_item.text.value
            
            # 构建响应
            response = {
                "response": assistant_text,
                "tools_used": "quark_search"
            }
            
            return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="non_streaming:app", host="0.0.0.0", port=8000, reload=False)