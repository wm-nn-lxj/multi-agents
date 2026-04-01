"""
上下文管理器 - 分层上下文管理与压缩
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging
import json

from config import ContextConfig, config


logger = logging.getLogger("context_manager")


class ContextLayer(BaseModel):
    """上下文层"""
    name: str
    content: dict
    tokens: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, config: ContextConfig = None):
        from config import config as global_config
        self.config = config or global_config.context
        
        # 分层上下文存储
        self.layers: dict[str, ContextLayer] = {
            "global": ContextLayer(name="global", content={}),
            "session": ContextLayer(name="session", content={}),
            "task": ContextLayer(name="task", content={}),
            "memory": ContextLayer(name="memory", content={})
        }
        
        # 层级大小限制
        self.layer_limits = {
            "global": self.config.global_layer_max,
            "session": self.config.session_layer_max,
            "task": self.config.task_layer_max,
            "memory": self.config.memory_layer_max
        }
    
    def update_layer(self, layer_name: str, content: dict):
        """更新指定层"""
        if layer_name not in self.layers:
            raise ValueError(f"未知的上下文层: {layer_name}")
        
        layer = self.layers[layer_name]
        layer.content = content
        layer.tokens = self._estimate_tokens(content)
        layer.last_accessed = datetime.now()
        
        # 检查是否超限
        if layer.tokens > self.layer_limits[layer_name]:
            self._compress_layer(layer_name)
    
    def get_layer(self, layer_name: str) -> dict:
        """获取指定层内容"""
        if layer_name not in self.layers:
            raise ValueError(f"未知的上下文层: {layer_name}")
        
        layer = self.layers[layer_name]
        layer.last_accessed = datetime.now()
        return layer.content
    
    def get_combined_context(
        self,
        include_global: bool = True,
        include_session: bool = True,
        include_task: bool = True,
        include_memory: bool = True
    ) -> dict:
        """获取组合上下文"""
        combined = {}
        
        if include_global:
            combined.update(self.layers["global"].content)
        if include_memory:
            combined.update(self.layers["memory"].content)
        if include_session:
            combined.update(self.layers["session"].content)
        if include_task:
            combined.update(self.layers["task"].content)
        
        return combined
    
    def get_total_tokens(self) -> int:
        """获取总token数"""
        return sum(layer.tokens for layer in self.layers.values())
    
    def is_within_limit(self) -> bool:
        """检查是否在限制内"""
        return self.get_total_tokens() <= self.config.max_total_tokens
    
    def _estimate_tokens(self, content: dict) -> int:
        """估算token数"""
        text = json.dumps(content, ensure_ascii=False)
        # 粗略估算: 1 token ≈ 4 字符 (中文) 或 0.75 单词 (英文)
        return len(text) // 2
    
    def _compress_layer(self, layer_name: str):
        """压缩指定层"""
        layer = self.layers[layer_name]
        
        if layer_name == "session":
            # 会话层压缩: 保留最近对话，历史生成摘要
            content = layer.content
            if "history" in content and len(content["history"]) > 10:
                recent = content["history"][-5:]
                summary = self._generate_summary(content["history"][:-5])
                content["history"] = [
                    {"type": "summary", "content": summary}
                ] + recent
                layer.content = content
                layer.tokens = self._estimate_tokens(content)
        
        elif layer_name == "task":
            # 任务层压缩: 只保留当前任务
            content = layer.content
            if "completed_tasks" in content:
                # 归档已完成任务
                content["archived"] = len(content.get("completed_tasks", []))
                content["completed_tasks"] = []
                layer.content = content
                layer.tokens = self._estimate_tokens(content)
        
        logger.info(f"上下文层 {layer_name} 已压缩: {layer.tokens} tokens")
    
    def _generate_summary(self, history: list) -> str:
        """生成历史摘要"""
        # 简化实现: 实际应调用LLM生成摘要
        return f"[历史对话摘要: {len(history)}条消息]"
    
    def clear_layer(self, layer_name: str):
        """清空指定层"""
        if layer_name in self.layers:
            self.layers[layer_name].content = {}
            self.layers[layer_name].tokens = 0
    
    def clear_all(self):
        """清空所有层"""
        for layer_name in self.layers:
            self.clear_layer(layer_name)
    
    def get_status(self) -> dict:
        """获取上下文状态"""
        return {
            "total_tokens": self.get_total_tokens(),
            "within_limit": self.is_within_limit(),
            "layers": {
                name: {
                    "tokens": layer.tokens,
                    "limit": self.layer_limits[name],
                    "utilization": layer.tokens / self.layer_limits[name] if self.layer_limits[name] > 0 else 0
                }
                for name, layer in self.layers.items()
            }
        }


class AgentContextManager:
    """Agent专用上下文管理器"""
    
    def __init__(self, agent_type: str, shared_context: ContextManager):
        self.agent_type = agent_type
        self.shared = shared_context
        self.local_context: list[dict] = []
        self.max_local = 20  # 最大本地消息数
    
    def add_message(self, role: str, content: str):
        """添加消息到本地上下文"""
        self.local_context.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 检查是否需要压缩
        if len(self.local_context) > self.max_local:
            self._compress_local()
    
    def get_messages_for_llm(self) -> list[dict]:
        """获取用于LLM的消息列表"""
        messages = []
        
        # 添加全局上下文
        global_ctx = self.shared.get_layer("global")
        if global_ctx.get("system_prompt"):
            messages.append({
                "role": "system",
                "content": global_ctx["system_prompt"]
            })
        
        # 添加记忆上下文
        memory_ctx = self.shared.get_layer("memory")
        if memory_ctx.get("relevant_memories"):
            messages.append({
                "role": "system",
                "content": f"相关记忆:\n{memory_ctx['relevant_memories']}"
            })
        
        # 添加本地对话
        for msg in self.local_context:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return messages
    
    def _compress_local(self):
        """压缩本地上下文"""
        if len(self.local_context) <= 4:
            return
        
        # 保留最近的消息
        recent = self.local_context[-4:]
        history = self.local_context[:-4]
        
        # 生成摘要
        summary = f"[历史消息摘要: {len(history)}条]"
        
        self.local_context = [
            {"role": "system", "content": summary}
        ] + recent
    
    def clear(self):
        """清空本地上下文"""
        self.local_context = []
