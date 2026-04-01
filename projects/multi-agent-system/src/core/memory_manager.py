"""
记忆管理器 - 短期记忆(Redis) + 长期记忆(向量数据库)
"""
import json
from typing import Optional, Any
from datetime import datetime, timedelta
import logging
import asyncio
from pydantic import BaseModel, Field

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from config import MemoryConfig, config


logger = logging.getLogger("memory_manager")


class MemoryItem(BaseModel):
    """记忆项"""
    id: str
    content: str
    metadata: dict = {}
    created_at: datetime = Field(default_factory=datetime.now)
    embedding: Optional[list[float]] = None


class ShortTermMemory:
    """短期记忆 - Redis实现"""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self):
        """连接Redis"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis库未安装，短期记忆功能不可用")
            return False
        
        try:
            self.client = redis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.client.ping()
            self._connected = True
            logger.info("Redis连接成功")
            return True
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            self._connected = False
            return False
    
    async def store(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """存储记忆"""
        if not self._connected or not self.client:
            return False
        
        try:
            serialized = json.dumps(value, ensure_ascii=False, default=str)
            await self.client.setex(
                key,
                ttl or self.config.redis_ttl,
                serialized
            )
            return True
        except Exception as e:
            logger.error(f"短期记忆存储失败: {e}")
            return False
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """检索记忆"""
        if not self._connected or not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"短期记忆检索失败: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """删除记忆"""
        if not self._connected or not self.client:
            return False
        
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"短期记忆删除失败: {e}")
            return False
    
    async def list_keys(self, pattern: str = "*") -> list[str]:
        """列出匹配的键"""
        if not self._connected or not self.client:
            return []
        
        try:
            keys = await self.client.keys(pattern)
            return keys
        except Exception as e:
            logger.error(f"列出键失败: {e}")
            return []
    
    async def close(self):
        """关闭连接"""
        if self.client:
            await self.client.close()


class LongTermMemory:
    """长期记忆 - ChromaDB向量数据库"""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.client: Optional[chromadb.Client] = None
        self.collection = None
        self._connected = False
    
    def connect(self):
        """连接向量数据库"""
        if not CHROMA_AVAILABLE:
            logger.warning("ChromaDB库未安装，长期记忆功能不可用")
            return False
        
        try:
            self.client = chromadb.PersistentClient(
                path=self.config.vector_db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name="agent_memories",
                metadata={"hnsw:space": "cosine"}
            )
            self._connected = True
            logger.info(f"ChromaDB连接成功: {self.config.vector_db_path}")
            return True
        except Exception as e:
            logger.warning(f"ChromaDB连接失败: {e}")
            self._connected = False
            return False
    
    def store(self, id: str, content: str, metadata: Optional[dict] = None) -> bool:
        """存储记忆"""
        if not self._connected or not self.collection:
            return False
        
        try:
            self.collection.add(
                ids=[id],
                documents=[content],
                metadatas=[metadata or {}]
            )
            return True
        except Exception as e:
            logger.error(f"长期记忆存储失败: {e}")
            return False
    
    def search(
        self,
        query: str,
        n_results: Optional[int] = None,
        where: Optional[dict] = None
    ) -> list[dict]:
        """语义搜索"""
        if not self._connected or not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results or self.config.top_k,
                where=where
            )
            
            memories = []
            for i, doc in enumerate(results["documents"][0]):
                memories.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0
                })
            
            # 过滤低相似度结果
            memories = [
                m for m in memories 
                if m["distance"] < (1 - self.config.min_score)
            ]
            
            return memories
        except Exception as e:
            logger.error(f"长期记忆搜索失败: {e}")
            return []
    
    def delete(self, id: str) -> bool:
        """删除记忆"""
        if not self._connected or not self.collection:
            return False
        
        try:
            self.collection.delete(ids=[id])
            return True
        except Exception as e:
            logger.error(f"长期记忆删除失败: {e}")
            return False
    
    def count(self) -> int:
        """获取记忆数量"""
        if not self._connected or not self.collection:
            return 0
        return self.collection.count()


class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, config: MemoryConfig = None):
        self.config = config or config.memory
        self.short_term = ShortTermMemory(self.config)
        self.long_term = LongTermMemory(self.config)
        self._initialized = False
    
    async def initialize(self) -> bool:
        """初始化记忆系统"""
        # 连接短期记忆
        await self.short_term.connect()
        
        # 连接长期记忆
        self.long_term.connect()
        
        self._initialized = True
        logger.info("记忆管理器初始化完成")
        return True
    
    async def remember(
        self,
        content: str,
        metadata: Optional[dict] = None,
        permanent: bool = False
    ) -> str:
        """存储记忆"""
        import uuid
        memory_id = f"mem_{uuid.uuid4().hex[:12]}"
        
        # 存储到短期记忆
        await self.short_term.store(
            memory_id,
            {
                "content": content,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat()
            }
        )
        
        # 如果是永久记忆，同时存储到长期记忆
        if permanent:
            self.long_term.store(
                memory_id,
                content,
                {
                    **(metadata or {}),
                    "created_at": datetime.now().isoformat()
                }
            )
        
        return memory_id
    
    async def recall(self, query: str, use_semantic: bool = True) -> list[dict]:
        """检索记忆"""
        results = []
        
        # 语义搜索长期记忆
        if use_semantic:
            long_term_results = self.long_term.search(query)
            results.extend(long_term_results)
        
        # 关键词搜索短期记忆
        short_term_keys = await self.short_term.list_keys("mem_*")
        for key in short_term_keys[:10]:  # 限制搜索数量
            memory = await self.short_term.retrieve(key)
            if memory and query.lower() in memory.get("content", "").lower():
                results.append({
                    "id": key,
                    "content": memory["content"],
                    "metadata": memory.get("metadata", {}),
                    "source": "short_term"
                })
        
        return results
    
    async def forget(self, memory_id: str) -> bool:
        """删除记忆"""
        # 从短期记忆删除
        await self.short_term.delete(memory_id)
        
        # 从长期记忆删除
        self.long_term.delete(memory_id)
        
        return True
    
    async def store_agent_state(self, agent_type: str, state: dict) -> bool:
        """存储Agent状态"""
        key = f"agent_state:{agent_type}"
        return await self.short_term.store(key, state, ttl=3600)
    
    async def get_agent_state(self, agent_type: str) -> Optional[dict]:
        """获取Agent状态"""
        key = f"agent_state:{agent_type}"
        return await self.short_term.retrieve(key)
    
    async def close(self):
        """关闭连接"""
        await self.short_term.close()
    
    def get_status(self) -> dict:
        """获取记忆系统状态"""
        return {
            "short_term": {
                "connected": self.short_term._connected,
                "type": "redis"
            },
            "long_term": {
                "connected": self.long_term._connected,
                "count": self.long_term.count(),
                "type": "chroma"
            }
        }
