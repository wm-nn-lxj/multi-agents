"""
多Agent协作系统 - 全局配置
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class AgentType(str, Enum):
    """Agent类型枚举"""
    PRODUCT = "product"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"


class LLMConfig(BaseModel):
    """LLM配置"""
    provider: str = Field(default="openai", description="LLM提供商")
    model: str = Field(default="gpt-4", description="模型名称")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: int = Field(default=4096, description="最大输出tokens")
    
    # Token预算配置 - 更新为198K
    max_context_tokens: int = Field(default=198000, description="最大上下文tokens")
    max_task_tokens: int = Field(default=50000, description="单任务最大tokens")
    
    class Config:
        env_prefix = "LLM_"


class ContextConfig(BaseModel):
    """上下文管理配置"""
    # 分层上下文大小限制 - 总计198K
    global_layer_max: int = Field(default=10000, description="全局层最大tokens")
    session_layer_max: int = Field(default=100000, description="会话层最大tokens")
    task_layer_max: int = Field(default=50000, description="任务层最大tokens")
    memory_layer_max: int = Field(default=38000, description="记忆层最大tokens")
    
    # 总上下文限制
    max_total_tokens: int = Field(default=198000, description="总上下文最大tokens")
    
    # 压缩策略
    compression_threshold: float = Field(default=0.85, description="压缩触发阈值(占比)")
    summary_ratio: float = Field(default=0.3, description="摘要压缩比例")
    
    class Config:
        env_prefix = "CONTEXT_"


class MemoryConfig(BaseModel):
    """记忆管理配置"""
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    redis_ttl: int = Field(default=86400, description="短期记忆TTL(秒)")
    
    vector_db_type: str = Field(default="chroma", description="向量数据库类型")
    vector_db_path: str = Field(default="./data/chroma", description="向量数据库路径")
    embedding_model: str = Field(default="text-embedding-ada-002", description="嵌入模型")
    
    # 检索配置
    top_k: int = Field(default=5, description="检索返回数量")
    min_score: float = Field(default=0.7, description="最小相似度阈值")
    
    class Config:
        env_prefix = "MEMORY_"


class TaskConfig(BaseModel):
    """任务执行配置"""
    # 执行评估阈值
    min_success_probability: float = Field(default=0.7, description="最小完成概率")
    max_token_budget: int = Field(default=100000, description="单任务Token预算")
    max_execution_time: int = Field(default=300, description="最大执行时间(秒)")
    
    # 重试配置
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delay: int = Field(default=5, description="重试延迟(秒)")
    
    class Config:
        env_prefix = "TASK_"


class AgentConfig(BaseModel):
    """单个Agent配置"""
    agent_type: AgentType
    name: str
    description: str
    system_prompt: str
    skills: list[str] = Field(default_factory=list)
    max_history: int = Field(default=20, description="最大历史消息数")
    
    # 可选独立LLM配置
    llm_config: Optional[LLMConfig] = None


class SystemConfig(BaseModel):
    """系统总配置"""
    # 共享LLM配置
    shared_llm: LLMConfig = Field(default_factory=LLMConfig)
    
    # 各模块配置
    context: ContextConfig = Field(default_factory=ContextConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    task: TaskConfig = Field(default_factory=TaskConfig)
    
    # Agent配置列表
    agents: dict[AgentType, AgentConfig] = Field(default_factory=dict)
    
    # API服务配置
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    
    # 日志配置
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="./logs/agent_system.log")


def load_config() -> SystemConfig:
    """加载配置，支持环境变量覆盖"""
    config = SystemConfig()
    
    # 从环境变量加载LLM配置
    if os.getenv("OPENAI_API_KEY"):
        config.shared_llm.api_key = os.getenv("OPENAI_API_KEY")
    if os.getenv("OPENAI_BASE_URL"):
        config.shared_llm.base_url = os.getenv("OPENAI_BASE_URL")
    if os.getenv("LLM_MODEL"):
        config.shared_llm.model = os.getenv("LLM_MODEL")
    
    return config


# 全局配置实例
config = load_config()
