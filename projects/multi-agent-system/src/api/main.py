"""
API服务 - FastAPI实现
提供HTTP接口供外部调用
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any
import asyncio
import logging
from datetime import datetime
import uvicorn

from config import AgentType, config
from agents import ProductAgent, ArchitectAgent, DeveloperAgent, ReviewerAgent, TesterAgent
from core import MemoryManager, MessageBus, test_llm_connection


logger = logging.getLogger("api")

# 创建FastAPI应用
app = FastAPI(
    title="多Agent协作系统 API",
    description="提供多Agent协作开发的HTTP接口",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 请求模型 ============

class TaskRequest(BaseModel):
    """任务请求"""
    task: str
    context: Optional[dict] = None
    agent: Optional[str] = "product"


class ConfigRequest(BaseModel):
    """配置请求"""
    api_key: str
    base_url: Optional[str] = None
    model: Optional[str] = "gpt-4"


# ============ 全局实例 ============

agents: dict[AgentType, Any] = {}
memory_manager: Optional[MemoryManager] = None
message_bus: Optional[MessageBus] = None
system_ready = False


# ============ 生命周期 ============

@app.on_event("startup")
async def startup():
    """启动时初始化"""
    global memory_manager, message_bus, system_ready
    
    logger.info("系统启动中...")
    
    # 初始化记忆管理器
    memory_manager = MemoryManager()
    await memory_manager.initialize()
    
    # 初始化消息总线
    message_bus = MessageBus()
    await message_bus.start()
    
    # 初始化Agent（延迟，等待API配置）
    logger.info("系统初始化完成，等待LLM API配置")
    system_ready = True


@app.on_event("shutdown")
async def shutdown():
    """关闭时清理"""
    global memory_manager, message_bus
    
    logger.info("系统关闭中...")
    
    if message_bus:
        await message_bus.stop()
    
    if memory_manager:
        await memory_manager.close()
    
    logger.info("系统已关闭")


# ============ API端点 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "多Agent协作系统",
        "version": "1.0.0",
        "status": "running" if system_ready else "initializing"
    }


@app.get("/health")
async def health():
    """健康检查"""
    llm_ok, llm_msg = await test_llm_connection()
    
    return {
        "status": "healthy" if system_ready else "initializing",
        "llm": {
            "connected": llm_ok,
            "message": llm_msg
        },
        "memory": memory_manager.get_status() if memory_manager else None,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/config/llm")
async def configure_llm(config_req: ConfigRequest):
    """配置LLM API"""
    import os
    
    # 设置环境变量
    os.environ["OPENAI_API_KEY"] = config_req.api_key
    if config_req.base_url:
        os.environ["OPENAI_BASE_URL"] = config_req.base_url
    if config_req.model:
        os.environ["LLM_MODEL"] = config_req.model
    
    # 重新加载配置
    from config import load_config
    global config
    config = load_config()
    
    # 初始化Agent
    await _init_agents()
    
    # 测试连接
    ok, msg = await test_llm_connection()
    
    return {
        "success": ok,
        "message": msg,
        "model": config.shared_llm.model
    }


async def _init_agents():
    """初始化所有Agent"""
    global agents
    
    from core import get_llm_client
    
    llm = get_llm_client()
    
    agents[AgentType.PRODUCT] = ProductAgent(
        llm_client=llm,
        memory_manager=memory_manager,
        message_bus=message_bus
    )
    agents[AgentType.ARCHITECT] = ArchitectAgent(llm_client=llm)
    agents[AgentType.DEVELOPER] = DeveloperAgent(llm_client=llm)
    agents[AgentType.REVIEWER] = ReviewerAgent(llm_client=llm)
    agents[AgentType.TESTER] = TesterAgent(llm_client=llm)
    
    logger.info("所有Agent初始化完成")


@app.post("/task/execute")
async def execute_task(request: TaskRequest):
    """执行任务"""
    if not agents:
        raise HTTPException(status_code=503, detail="Agent未初始化，请先配置LLM API")
    
    # 获取目标Agent
    try:
        agent_type = AgentType(request.agent.lower())
    except:
        agent_type = AgentType.PRODUCT
    
    agent = agents.get(agent_type)
    if not agent:
        raise HTTPException(status_code=400, detail=f"未知的Agent类型: {request.agent}")
    
    # 执行任务
    context = request.context or {}
    result = await agent.execute(request.task, context)
    
    return {
        "success": result.success,
        "output": result.output,
        "tokens_used": result.tokens_used,
        "execution_time": result.execution_time,
        "error": result.error,
        "needs_human": result.needs_human,
        "human_message": result.human_message
    }


@app.post("/task/evaluate")
async def evaluate_task(request: TaskRequest):
    """评估任务"""
    if not agents:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    agent_type = AgentType.PRODUCT
    agent = agents.get(agent_type)
    
    if not agent:
        raise HTTPException(status_code=400, detail="Agent未找到")
    
    context = request.context or {}
    evaluation = await agent.evaluate_task(request.task, context)
    
    return {
        "can_execute": evaluation.can_execute,
        "success_probability": evaluation.success_probability,
        "token_estimate": evaluation.token_estimate,
        "time_estimate": evaluation.time_estimate,
        "reason": evaluation.reason
    }


@app.get("/agents/status")
async def get_agents_status():
    """获取所有Agent状态"""
    if not agents:
        return {"agents": [], "message": "Agent未初始化"}
    
    return {
        "agents": [
            agent.get_stats()
            for agent in agents.values()
        ]
    }


@app.get("/agents/{agent_type}/status")
async def get_agent_status(agent_type: str):
    """获取单个Agent状态"""
    try:
        at = AgentType(agent_type.lower())
    except:
        raise HTTPException(status_code=400, detail=f"未知的Agent类型: {agent_type}")
    
    agent = agents.get(at)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent未找到: {agent_type}")
    
    return agent.get_stats()


@app.post("/workflow/run")
async def run_workflow(request: TaskRequest, background_tasks: BackgroundTasks):
    """运行完整工作流"""
    if not agents:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    product_agent = agents.get(AgentType.PRODUCT)
    
    # 执行协调
    context = request.context or {}
    result = await product_agent.coordinate_execution(request.task, context)
    
    return {
        "workflow_started": True,
        "overview": result.get("overview"),
        "dispatch_results": result.get("dispatch_results")
    }


@app.get("/memory/status")
async def get_memory_status():
    """获取记忆系统状态"""
    if not memory_manager:
        return {"status": "not_initialized"}
    
    return memory_manager.get_status()


# ============ 启动函数 ============

def run_server():
    """运行API服务器"""
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level="info"
    )


if __name__ == "__main__":
    run_server()
