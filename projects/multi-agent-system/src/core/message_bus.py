"""
消息总线 - Agent间通信与协调
"""
import asyncio
from typing import Optional, Callable, Any
from datetime import datetime
from collections import defaultdict
import logging
import json

from config import AgentType


logger = logging.getLogger("message_bus")


class Message:
    """消息"""
    def __init__(
        self,
        sender: AgentType,
        receiver: AgentType,
        content: Any,
        msg_type: str = "task",
        metadata: Optional[dict] = None
    ):
        self.id = f"msg_{datetime.now().timestamp()}"
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.msg_type = msg_type
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.processed = False
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender": self.sender.value,
            "receiver": self.receiver.value,
            "content": self.content,
            "msg_type": self.msg_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "processed": self.processed
        }


class TaskMessage(Message):
    """任务消息"""
    def __init__(
        self,
        sender: AgentType,
        receiver: AgentType,
        task_id: str,
        task_type: str,
        task_data: dict,
        priority: int = 0
    ):
        super().__init__(
            sender=sender,
            receiver=receiver,
            content={
                "task_id": task_id,
                "task_type": task_type,
                "task_data": task_data
            },
            msg_type="task"
        )
        self.priority = priority


class ResultMessage(Message):
    """结果消息"""
    def __init__(
        self,
        sender: AgentType,
        receiver: AgentType,
        task_id: str,
        success: bool,
        result: Any,
        tokens_used: int = 0
    ):
        super().__init__(
            sender=sender,
            receiver=receiver,
            content={
                "task_id": task_id,
                "success": success,
                "result": result,
                "tokens_used": tokens_used
            },
            msg_type="result"
        )


class ControlMessage(Message):
    """控制消息"""
    def __init__(
        self,
        sender: AgentType,
        receiver: AgentType,
        command: str,
        params: Optional[dict] = None
    ):
        super().__init__(
            sender=sender,
            receiver=receiver,
            content={
                "command": command,
                "params": params or {}
            },
            msg_type="control"
        )


class MessageBus:
    """消息总线"""
    
    def __init__(self):
        # 每个Agent的消息队列
        self.queues: dict[AgentType, asyncio.Queue] = {
            agent_type: asyncio.Queue()
            for agent_type in AgentType
        }
        
        # 消息处理器
        self.handlers: dict[AgentType, Callable] = {}
        
        # 消息历史
        self.history: list[dict] = []
        self.max_history = 1000
        
        # 统计
        self.stats = defaultdict(lambda: {"sent": 0, "received": 0})
        
        # 运行状态
        self._running = False
        self._tasks: list[asyncio.Task] = []
    
    def register_handler(self, agent_type: AgentType, handler: Callable):
        """注册消息处理器"""
        self.handlers[agent_type] = handler
        logger.info(f"注册消息处理器: {agent_type.value}")
    
    async def send(self, message: Message) -> bool:
        """发送消息"""
        try:
            await self.queues[message.receiver].put(message)
            
            # 记录历史
            self.history.append(message.to_dict())
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
            
            # 更新统计
            self.stats[message.sender.value]["sent"] += 1
            
            logger.debug(f"消息发送: {message.sender.value} -> {message.receiver.value}")
            return True
        except Exception as e:
            logger.error(f"消息发送失败: {e}")
            return False
    
    async def receive(self, agent_type: AgentType, timeout: float = 1.0) -> Optional[Message]:
        """接收消息"""
        try:
            message = await asyncio.wait_for(
                self.queues[agent_type].get(),
                timeout=timeout
            )
            self.stats[agent_type.value]["received"] += 1
            return message
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"消息接收失败: {e}")
            return None
    
    async def broadcast(self, sender: AgentType, content: Any, exclude: list[AgentType] = None):
        """广播消息"""
        exclude = exclude or []
        for agent_type in AgentType:
            if agent_type != sender and agent_type not in exclude:
                await self.send(Message(
                    sender=sender,
                    receiver=agent_type,
                    content=content,
                    msg_type="broadcast"
                ))
    
    async def start(self):
        """启动消息总线"""
        self._running = True
        logger.info("消息总线启动")
    
    async def stop(self):
        """停止消息总线"""
        self._running = False
        for task in self._tasks:
            task.cancel()
        logger.info("消息总线停止")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return dict(self.stats)
    
    def get_history(self, limit: int = 100) -> list[dict]:
        """获取消息历史"""
        return self.history[-limit:]


class Coordinator:
    """协调器 - Product Agent专用"""
    
    def __init__(self, message_bus: MessageBus):
        self.bus = message_bus
        self.pending_tasks: dict[str, dict] = {}
        self.completed_tasks: dict[str, dict] = {}
        self.agent_status: dict[AgentType, str] = {
            agent_type: "idle" for agent_type in AgentType
        }
    
    async def dispatch_task(
        self,
        task_id: str,
        task_type: str,
        target_agent: AgentType,
        task_data: dict,
        priority: int = 0
    ) -> bool:
        """分发任务"""
        # 记录待处理任务
        self.pending_tasks[task_id] = {
            "type": task_type,
            "target": target_agent.value,
            "data": task_data,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # 发送任务消息
        message = TaskMessage(
            sender=AgentType.PRODUCT,
            receiver=target_agent,
            task_id=task_id,
            task_type=task_type,
            task_data=task_data,
            priority=priority
        )
        
        return await self.bus.send(message)
    
    async def handle_result(self, result: ResultMessage):
        """处理结果"""
        task_id = result.content["task_id"]
        
        if task_id in self.pending_tasks:
            # 移动到已完成
            self.completed_tasks[task_id] = {
                **self.pending_tasks[task_id],
                "result": result.content["result"],
                "success": result.content["success"],
                "tokens_used": result.content["tokens_used"],
                "completed_at": datetime.now().isoformat()
            }
            del self.pending_tasks[task_id]
    
    def update_agent_status(self, agent_type: AgentType, status: str):
        """更新Agent状态"""
        self.agent_status[agent_type] = status
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        if task_id in self.pending_tasks:
            return {"status": "pending", **self.pending_tasks[task_id]}
        elif task_id in self.completed_tasks:
            return {"status": "completed", **self.completed_tasks[task_id]}
        return None
    
    def get_overview(self) -> dict:
        """获取整体概览"""
        return {
            "pending_tasks": len(self.pending_tasks),
            "completed_tasks": len(self.completed_tasks),
            "agent_status": {
                agent.value: status 
                for agent, status in self.agent_status.items()
            }
        }
