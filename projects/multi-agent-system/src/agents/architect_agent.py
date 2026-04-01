"""
Architect Agent - 架构设计Agent
负责架构设计、技术选型、方案评审
"""
from typing import Optional
import json
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AgentType
from core import BaseAgent, TaskResult, LLMClient, get_llm_client


logger = logging.getLogger("agents.architect")


class ArchitectAgent(BaseAgent):
    """架构设计Agent"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        super().__init__(
            agent_type=AgentType.ARCHITECT,
            name="Architect Agent",
            description="负责架构设计、技术选型和方案评审"
        )
        self.llm = llm_client or get_llm_client()
    
    def get_system_prompt(self) -> str:
        return """你是Architect Agent，负责系统架构设计。

## 核心职责
1. **架构设计**: 设计系统整体架构，包括模块划分、接口定义、数据流
2. **技术选型**: 评估和推荐技术栈，对比分析优劣
3. **方案评审**: 评估方案可行性，识别风险
4. **性能规划**: 设计性能优化方案，预估系统容量

## 设计原则
- 高内聚低耦合
- 可扩展可维护
- 安全可靠
- 性能优先

## 输出格式
使用Markdown格式，包含:
- 架构图描述（可用Mermaid语法）
- 模块说明
- 接口定义
- 技术选型理由
- 风险评估"""
    
    async def execute(self, task: str, context: dict) -> TaskResult:
        """执行架构设计任务"""
        self.state = "working"
        
        try:
            # 分析任务类型
            task_lower = task.lower()
            
            if "架构" in task or "architecture" in task_lower:
                result = await self._design_architecture(task, context)
            elif "技术选型" in task or "tech stack" in task_lower:
                result = await self._tech_selection(task, context)
            elif "评审" in task or "review" in task_lower:
                result = await self._review_solution(task, context)
            else:
                result = await self._general_design(task, context)
            
            self.success_count += 1
            
            return TaskResult(
                success=True,
                output=result,
                tokens_used=self.total_tokens
            )
        
        except Exception as e:
            logger.error(f"架构设计失败: {e}")
            return TaskResult(
                success=False,
                output=None,
                error=str(e)
            )
        
        finally:
            self.state = "idle"
            self.task_count += 1
    
    async def _design_architecture(self, requirement: str, context: dict) -> str:
        """设计架构"""
        prompt = f"""设计系统架构:

## 需求
{requirement}

## 上下文
{json.dumps(context, ensure_ascii=False, indent=2)}

## 输出要求
1. 系统架构图（使用Mermaid语法）
2. 核心模块说明
3. 接口定义
4. 数据流设计
5. 部署架构建议"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=4000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _tech_selection(self, requirement: str, context: dict) -> str:
        """技术选型"""
        prompt = f"""进行技术选型分析:

## 需求
{requirement}

## 上下文
{json.dumps(context, ensure_ascii=False, indent=2)}

## 输出要求
1. 候选技术方案对比表
2. 推荐方案及理由
3. 风险评估
4. 实施建议"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _review_solution(self, solution: str, context: dict) -> str:
        """评审方案"""
        prompt = f"""评审以下技术方案:

## 方案描述
{solution}

## 上下文
{json.dumps(context, ensure_ascii=False, indent=2)}

## 评审要点
1. 可行性分析
2. 性能评估
3. 安全性检查
4. 可维护性评估
5. 风险识别
6. 改进建议"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _general_design(self, task: str, context: dict) -> str:
        """通用设计"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": task}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
