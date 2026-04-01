"""
Developer Agent - 代码开发Agent
负责代码实现、重构、文档编写
"""
from typing import Optional
import json
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AgentType
from core import BaseAgent, TaskResult, LLMClient, get_llm_client


logger = logging.getLogger("agents.developer")


class DeveloperAgent(BaseAgent):
    """代码开发Agent"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        super().__init__(
            agent_type=AgentType.DEVELOPER,
            name="Developer Agent",
            description="负责代码实现、重构和文档编写"
        )
        self.llm = llm_client or get_llm_client()
    
    def get_system_prompt(self) -> str:
        return """你是Developer Agent，负责代码实现。

## 核心职责
1. **代码实现**: 根据设计文档实现功能代码
2. **代码重构**: 优化代码结构，提升可维护性
3. **单元测试**: 编写单元测试代码
4. **文档编写**: 编写技术文档和注释

## 编码规范
- 遵循PEP8/ESLint等规范
- 函数单一职责
- 有意义的命名
- 适当的注释
- 错误处理完善

## 输出格式
使用Markdown代码块，标注语言类型:
```python
# 代码实现
```

同时提供:
- 代码说明
- 使用示例
- 注意事项"""
    
    async def execute(self, task: str, context: dict) -> TaskResult:
        """执行开发任务"""
        self.state = "working"
        
        try:
            task_lower = task.lower()
            
            if "实现" in task or "implement" in task_lower or "开发" in task:
                result = await self._implement_feature(task, context)
            elif "重构" in task or "refactor" in task_lower:
                result = await self._refactor_code(task, context)
            elif "测试" in task or "test" in task_lower:
                result = await self._write_tests(task, context)
            elif "文档" in task or "document" in task_lower:
                result = await self._write_documentation(task, context)
            else:
                result = await self._general_development(task, context)
            
            self.success_count += 1
            
            return TaskResult(
                success=True,
                output=result,
                tokens_used=self.total_tokens
            )
        
        except Exception as e:
            logger.error(f"开发任务失败: {e}")
            return TaskResult(
                success=False,
                output=None,
                error=str(e)
            )
        
        finally:
            self.state = "idle"
            self.task_count += 1
    
    async def _implement_feature(self, requirement: str, context: dict) -> str:
        """实现功能"""
        # 提取技术栈
        tech_stack = context.get("tech_stack", "Python")
        
        prompt = f"""实现以下功能:

## 需求描述
{requirement}

## 技术栈
{tech_stack}

## 上下文
{json.dumps(context, ensure_ascii=False, indent=2)}

## 输出要求
1. 完整可运行的代码
2. 包含错误处理
3. 添加必要注释
4. 提供使用示例"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=4000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _refactor_code(self, code: str, context: dict) -> str:
        """重构代码"""
        prompt = f"""重构以下代码:

## 原始代码
```
{code}
```

## 重构目标
- 提升可读性
- 减少重复
- 优化性能
- 增强可维护性

## 输出要求
1. 重构后的代码
2. 重构说明
3. 改进点列表"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=4000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _write_tests(self, code: str, context: dict) -> str:
        """编写测试"""
        prompt = f"""为以下代码编写单元测试:

## 代码
```
{code}
```

## 测试框架
pytest

## 输出要求
1. 完整的测试代码
2. 覆盖正常场景
3. 覆盖异常场景
4. 边界条件测试"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _write_documentation(self, code: str, context: dict) -> str:
        """编写文档"""
        prompt = f"""为以下代码编写技术文档:

## 代码
```
{code}
```

## 文档要求
1. 功能说明
2. API文档
3. 使用示例
4. 注意事项"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=2000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _general_development(self, task: str, context: dict) -> str:
        """通用开发"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": task}
        ]
        
        response = await self.llm.chat(messages, max_tokens=4000)
        self.total_tokens += response.tokens_used
        
        return response.content
