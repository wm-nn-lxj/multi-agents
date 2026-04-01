"""
Agent基类 - 定义Agent核心接口和行为
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
import logging

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AgentType, LLMConfig, config


class AgentState(str, Enum):
    """Agent状态"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"


class Message(BaseModel):
    """Agent间消息"""
    id: str = Field(default_factory=lambda: f"msg_{datetime.now().timestamp()}")
    sender: AgentType
    receiver: AgentType
    content: str
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    reply_to: Optional[str] = None


class TaskResult(BaseModel):
    """任务执行结果"""
    success: bool
    output: Any
    tokens_used: int = 0
    execution_time: float = 0.0
    error: Optional[str] = None
    needs_human: bool = False
    human_message: Optional[str] = None


class TaskEvaluation(BaseModel):
    """任务执行评估"""
    success_probability: float
    token_estimate: int
    time_estimate: float
    can_execute: bool
    reason: Optional[str] = None


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(
        self,
        agent_type: AgentType,
        name: str,
        description: str,
        llm_config: Optional[LLMConfig] = None
    ):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.state = AgentState.IDLE
        self.llm_config = llm_config or config.shared_llm
        self.logger = logging.getLogger(f"agent.{agent_type.value}")
        
        # 上下文管理
        self.context: list[dict] = []
        self.max_context_size = config.context.session_layer_max
        
        # 消息队列
        self.message_queue: asyncio.Queue[Message] = asyncio.Queue()
        
        # 统计信息
        self.total_tokens = 0
        self.task_count = 0
        self.success_count = 0
    
    @abstractmethod
    async def execute(self, task: str, context: dict) -> TaskResult:
        """执行任务 - 子类实现"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词 - 子类实现"""
        pass
    
    async def evaluate_task(self, task: str, context: dict) -> TaskEvaluation:
        """评估任务是否可执行"""
        # 基础评估逻辑
        # 估算token消耗
        task_tokens = len(task.split()) * 2  # 粗略估算
        context_tokens = sum(
            len(str(v).split()) * 2 
            for v in context.values()
        )
        total_estimate = task_tokens + context_tokens
        
        # 评估完成概率（基于历史）
        success_rate = (
            self.success_count / self.task_count 
            if self.task_count > 0 else 0.8
        )
        
        # 判断是否可执行
        can_execute = (
            success_rate >= config.task.min_success_probability and
            total_estimate <= config.task.max_token_budget
        )
        
        reason = None
        if not can_execute:
            if success_rate < config.task.min_success_probability:
                reason = f"完成概率({success_rate:.2%})低于阈值({config.task.min_success_probability:.2%})"
            elif total_estimate > config.task.max_token_budget:
                reason = f"Token估算({total_estimate})超出预算({config.task.max_token_budget})"
        
        return TaskEvaluation(
            success_probability=success_rate,
            token_estimate=total_estimate,
            time_estimate=total_estimate / 100,  # 粗略估算
            can_execute=can_execute,
            reason=reason
        )
    
    async def send_message(self, receiver: AgentType, content: str, metadata: dict = None):
        """发送消息给其他Agent"""
        message = Message(
            sender=self.agent_type,
            receiver=receiver,
            content=content,
            metadata=metadata or {}
        )
        # 通过消息总线发送（由协调器实现）
        return message
    
    async def receive_message(self) -> Message:
        """接收消息"""
        return await self.message_queue.get()
    
    def update_context(self, new_context: dict):
        """更新上下文，自动管理大小"""
        self.context.append({
            "content": new_context,
            "timestamp": datetime.now().isoformat()
        })
        
        # 检查是否需要压缩
        current_size = self._estimate_context_size()
        if current_size > self.max_context_size * config.context.compression_threshold:
            self._compress_context()
    
    def _estimate_context_size(self) -> int:
        """估算上下文大小"""
        return sum(
            len(str(item).split()) * 2
            for item in self.context
        )
    
    def _compress_context(self):
        """压缩上下文"""
        if len(self.context) <= 2:
            return
        
        # 保留最近的消息，对历史进行摘要压缩
        recent = self.context[-5:]
        history = self.context[:-5]
        
        # 生成摘要（实际实现需要调用LLM）
        summary = {
            "type": "summary",
            "content": f"[历史对话摘要: {len(history)}条消息已压缩]",
            "timestamp": datetime.now().isoformat()
        }
        
        self.context = [summary] + recent
        self.logger.info(f"上下文已压缩: {len(history)+5} -> {len(self.context)}")
    
    def clear_context(self):
        """清空上下文"""
        self.context = []
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "agent_type": self.agent_type.value,
            "state": self.state.value,
            "total_tokens": self.total_tokens,
            "task_count": self.task_count,
            "success_count": self.success_count,
            "success_rate": self.success_count / self.task_count if self.task_count > 0 else 0
        }
