"""
Product Agent - 产品管理Agent
负责需求分析、任务分解、协调调度、进度管理
"""
import asyncio
from typing import Optional, Any
from datetime import datetime
import json
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AgentType
from core import (
    BaseAgent, TaskResult, TaskEvaluation,
    LLMClient, get_llm_client,
    ContextManager, MemoryManager,
    MessageBus, Coordinator, TaskMessage, ResultMessage
)


logger = logging.getLogger("agents.product")


class ProductAgent(BaseAgent):
    """产品管理Agent - 协调者"""
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        context_manager: Optional[ContextManager] = None,
        memory_manager: Optional[MemoryManager] = None,
        message_bus: Optional[MessageBus] = None
    ):
        super().__init__(
            agent_type=AgentType.PRODUCT,
            name="Product Agent",
            description="负责产品定义、任务分解和协调调度"
        )
        
        self.llm = llm_client or get_llm_client()
        self.context_mgr = context_manager or ContextManager()
        self.memory_mgr = memory_manager or MemoryManager()
        self.bus = message_bus or MessageBus()
        self.coordinator = Coordinator(self.bus)
        
        # 任务队列
        self.task_queue: list[dict] = []
        self.current_task: Optional[dict] = None
    
    def get_system_prompt(self) -> str:
        return """你是Product Agent，负责产品管理和任务协调。

## 核心职责
1. **需求分析**: 解析用户需求，生成PRD文档
2. **任务分解**: 将需求拆解为可执行的子任务
3. **任务分配**: 将子任务分配给合适的专业Agent
4. **进度管理**: 跟踪任务执行状态，处理异常
5. **质量把控**: 确保交付物符合预期

## 可用Agent
- **Architect Agent**: 架构设计、技术选型
- **Developer Agent**: 代码实现、功能开发
- **Reviewer Agent**: 代码审查、质量把控
- **Tester Agent**: 测试设计、质量验证

## 任务分解原则
1. 单个任务粒度适中，可独立完成
2. 明确任务依赖关系
3. 设定合理的优先级
4. 评估任务复杂度和风险

## 执行评估
在执行任务前，评估:
- 完成概率 (需 > 70%)
- Token消耗 (需 < 预算)
- 时间预估 (需 < 截止时间)

不满足条件时，反馈人类决策。

## 输出格式
使用Markdown格式输出，结构清晰，重点突出。"""
    
    async def execute(self, task: str, context: dict) -> TaskResult:
        """执行任务"""
        start_time = datetime.now()
        self.state = "working"
        
        try:
            # 1. 分析任务类型
            task_type = await self._analyze_task_type(task)
            
            # 2. 根据类型执行不同逻辑
            if task_type == "prd":
                result = await self._generate_prd(task, context)
            elif task_type == "decompose":
                result = await self._decompose_task(task, context)
            elif task_type == "coordinate":
                result = await self._coordinate_execution(task, context)
            elif task_type == "report":
                result = await self._generate_report(task, context)
            else:
                result = await self._general_process(task, context)
            
            self.success_count += 1
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                success=True,
                output=result,
                tokens_used=self.total_tokens,
                execution_time=execution_time
            )
        
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            return TaskResult(
                success=False,
                output=None,
                error=str(e),
                needs_human=True,
                human_message=f"任务执行异常: {e}"
            )
        
        finally:
            self.state = "idle"
            self.task_count += 1
    
    async def _analyze_task_type(self, task: str) -> str:
        """分析任务类型"""
        prompt = f"""分析以下任务属于哪种类型，只返回类型名称:

任务: {task}

类型选项:
- prd: 生成PRD文档
- decompose: 分解任务
- coordinate: 协调执行
- report: 生成报告
- general: 一般处理

类型:"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=50)
        self.total_tokens += response.tokens_used
        
        return response.content.strip().lower()
    
    async def _generate_prd(self, requirement: str, context: dict) -> str:
        """生成PRD文档"""
        prompt = f"""根据以下需求生成PRD文档:

## 需求描述
{requirement}

## 上下文
{json.dumps(context, ensure_ascii=False, indent=2)}

## 输出要求
生成完整的PRD文档，包含:
1. 产品概述
2. 功能需求
3. 非功能需求
4. 技术方案建议
5. 验收标准

使用Markdown格式输出。"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=4000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _decompose_task(self, requirement: str, context: dict) -> dict:
        """分解任务"""
        prompt = f"""将以下需求分解为子任务:

## 需求描述
{requirement}

## 可用Agent
- Architect Agent: 架构设计
- Developer Agent: 代码开发
- Reviewer Agent: 代码审查
- Tester Agent: 测试验证

## 输出格式
返回JSON格式:
{{
  "tasks": [
    {{
      "id": "task_001",
      "type": "architecture|development|review|test",
      "agent": "architect|developer|reviewer|tester",
      "description": "任务描述",
      "priority": 1-5,
      "dependencies": ["task_id"],
      "estimated_tokens": 1000
    }}
  ],
  "workflow": "任务执行顺序说明"
}}"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=2000)
        self.total_tokens += response.tokens_used
        
        try:
            # 解析JSON
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except:
            return {"tasks": [], "workflow": "解析失败"}
    
    async def _coordinate_execution(self, task: str, context: dict) -> dict:
        """协调执行"""
        # 获取任务分解
        decomposition = await self._decompose_task(task, context)
        
        results = []
        for task_info in decomposition.get("tasks", []):
            # 评估任务
            evaluation = await self.evaluate_task(
                task_info["description"],
                context
            )
            
            if not evaluation.can_execute:
                results.append({
                    "task_id": task_info["id"],
                    "status": "blocked",
                    "reason": evaluation.reason
                })
                continue
            
            # 分发任务
            target_agent = AgentType(task_info["agent"])
            await self.coordinator.dispatch_task(
                task_id=task_info["id"],
                task_type=task_info["type"],
                target_agent=target_agent,
                task_data={
                    "description": task_info["description"],
                    "context": context
                },
                priority=task_info["priority"]
            )
            
            results.append({
                "task_id": task_info["id"],
                "status": "dispatched",
                "target": task_info["agent"]
            })
        
        return {
            "decomposition": decomposition,
            "dispatch_results": results,
            "overview": self.coordinator.get_overview()
        }
    
    async def _generate_report(self, task: str, context: dict) -> str:
        """生成报告"""
        overview = self.coordinator.get_overview()
        
        prompt = f"""生成项目进度报告:

## 项目状态
{json.dumps(overview, ensure_ascii=False, indent=2)}

## 请求
{task}

## 输出要求
生成清晰的进度报告，包含:
1. 整体进度
2. 各Agent状态
3. 任务完成情况
4. 风险和建议"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=2000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _general_process(self, task: str, context: dict) -> str:
        """一般处理"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": task}
        ]
        
        response = await self.llm.chat(messages)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def handle_result(self, result: ResultMessage):
        """处理其他Agent返回的结果"""
        await self.coordinator.handle_result(result)
        
        # 检查是否需要后续处理
        task_id = result.content["task_id"]
        if not result.content["success"]:
            logger.warning(f"任务 {task_id} 执行失败")
            # 可以触发重试或人工介入
    
    def get_status(self) -> dict:
        """获取状态"""
        return {
            **self.get_stats(),
            "coordinator": self.coordinator.get_overview(),
            "queue_size": len(self.task_queue)
        }
