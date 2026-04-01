"""
Tester Agent - 测试Agent
负责测试设计、测试执行、缺陷分析
"""
from typing import Optional
import json
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AgentType
from core import BaseAgent, TaskResult, LLMClient, get_llm_client


logger = logging.getLogger("agents.tester")


class TesterAgent(BaseAgent):
    """测试Agent"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        super().__init__(
            agent_type=AgentType.TESTER,
            name="Tester Agent",
            description="负责测试设计、测试执行和缺陷分析"
        )
        self.llm = llm_client or get_llm_client()
    
    def get_system_prompt(self) -> str:
        return """你是Tester Agent，负责软件测试。

## 核心职责
1. **测试设计**: 设计测试用例，制定测试策略
2. **测试执行**: 执行测试，记录结果
3. **缺陷分析**: 分析缺陷原因，定位问题
4. **质量报告**: 生成测试报告，提供质量评估

## 测试类型
- 功能测试
- 边界测试
- 异常测试
- 性能测试
- 安全测试

## 用例设计原则
- 覆盖正常流程
- 覆盖异常场景
- 覆盖边界条件
- 可重复执行
- 结果可验证

## 输出格式
使用Markdown格式:
- 测试用例表格
- 测试结果统计
- 缺陷列表
- 质量评估"""
    
    async def execute(self, task: str, context: dict) -> TaskResult:
        """执行测试任务"""
        self.state = "working"
        
        try:
            task_lower = task.lower()
            
            if "用例" in task or "case" in task_lower or "设计" in task:
                result = await self._design_test_cases(task, context)
            elif "执行" in task or "execute" in task_lower or "运行" in task:
                result = await self._execute_tests(task, context)
            elif "缺陷" in task or "bug" in task_lower or "分析" in task:
                result = await self._analyze_defects(task, context)
            elif "报告" in task or "report" in task_lower:
                result = await self._generate_report(task, context)
            else:
                result = await self._general_testing(task, context)
            
            self.success_count += 1
            
            return TaskResult(
                success=True,
                output=result,
                tokens_used=self.total_tokens
            )
        
        except Exception as e:
            logger.error(f"测试任务失败: {e}")
            return TaskResult(
                success=False,
                output=None,
                error=str(e)
            )
        
        finally:
            self.state = "idle"
            self.task_count += 1
    
    async def _design_test_cases(self, feature: str, context: dict) -> str:
        """设计测试用例"""
        prompt = f"""为以下功能设计测试用例:

## 功能描述
{feature}

## 上下文
{json.dumps(context, ensure_ascii=False, indent=2)}

## 输出要求
设计完整的测试用例，包含:

### 功能测试用例
| 用例ID | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|--------|---------|---------|---------|---------|--------|

### 边界测试用例
| 用例ID | 用例名称 | 边界条件 | 测试步骤 | 预期结果 |
|--------|---------|---------|---------|---------|

### 异常测试用例
| 用例ID | 用例名称 | 异常场景 | 测试步骤 | 预期结果 |
|--------|---------|---------|---------|---------|

### 测试覆盖率分析
- 功能覆盖: X%
- 场景覆盖: X%"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=4000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _execute_tests(self, test_info: str, context: dict) -> str:
        """执行测试"""
        prompt = f"""执行测试并生成结果:

## 测试信息
{test_info}

## 上下文
{json.dumps(context, ensure_ascii=False, indent=2)}

## 输出要求
### 测试执行结果
| 用例ID | 执行状态 | 实际结果 | 是否通过 | 备注 |
|--------|---------|---------|---------|------|

### 测试统计
- 总用例数: X
- 通过数: X
- 失败数: X
- 通过率: X%

### 失败用例分析
1. ...
2. ..."""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _analyze_defects(self, defect_info: str, context: dict) -> str:
        """分析缺陷"""
        prompt = f"""分析以下缺陷:

## 缺陷信息
{defect_info}

## 上下文
{json.dumps(context, ensure_ascii=False, indent=2)}

## 输出要求
### 缺陷分析报告

#### 缺陷描述
...

#### 根因分析
...

#### 影响范围
...

#### 复现步骤
1. ...
2. ...

#### 修复建议
...

#### 预防措施
..."""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _generate_report(self, test_summary: str, context: dict) -> str:
        """生成测试报告"""
        prompt = f"""生成测试报告:

## 测试概况
{test_summary}

## 上下文
{json.dumps(context, ensure_ascii=False, indent=2)}

## 输出要求
# 测试报告

## 1. 测试概述
- 测试范围
- 测试环境
- 测试时间

## 2. 测试结果统计
| 指标 | 数值 |
|-----|------|
| 用例总数 | X |
| 通过数 | X |
| 失败数 | X |
| 阻塞数 | X |
| 通过率 | X% |

## 3. 缺陷统计
| 严重程度 | 数量 | 已修复 | 待修复 |
|---------|------|--------|--------|

## 4. 质量评估
- 功能完整性: X/10
- 稳定性: X/10
- 性能: X/10

## 5. 风险与建议
...

## 6. 结论
..."""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _general_testing(self, task: str, context: dict) -> str:
        """通用测试"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": task}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
