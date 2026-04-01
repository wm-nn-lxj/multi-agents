"""
Reviewer Agent - 代码审查Agent
负责代码审查、安全审计、性能分析
"""
from typing import Optional
import json
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AgentType
from core import BaseAgent, TaskResult, LLMClient, get_llm_client


logger = logging.getLogger("agents.reviewer")


class ReviewerAgent(BaseAgent):
    """代码审查Agent"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        super().__init__(
            agent_type=AgentType.REVIEWER,
            name="Reviewer Agent",
            description="负责代码审查、安全审计和性能分析"
        )
        self.llm = llm_client or get_llm_client()
    
    def get_system_prompt(self) -> str:
        return """你是Reviewer Agent，负责代码审查。

## 核心职责
1. **代码审查**: 检查代码逻辑、风格、最佳实践
2. **安全审计**: 识别安全漏洞和风险
3. **性能分析**: 发现性能瓶颈，提供优化建议
4. **规范检查**: 确保代码符合编码规范

## 审查要点
### 代码质量
- 逻辑正确性
- 代码可读性
- 命名规范
- 注释完整性

### 安全性
- SQL注入
- XSS攻击
- 敏感数据泄露
- 权限控制

### 性能
- 算法复杂度
- 资源使用
- 并发安全
- 内存泄漏

## 输出格式
使用Markdown格式:
- 问题列表（按严重程度分类）
- 具体位置和描述
- 修复建议
- 总体评分"""
    
    async def execute(self, task: str, context: dict) -> TaskResult:
        """执行审查任务"""
        self.state = "working"
        
        try:
            task_lower = task.lower()
            
            if "审查" in task or "review" in task_lower:
                result = await self._review_code(task, context)
            elif "安全" in task or "security" in task_lower:
                result = await self._security_audit(task, context)
            elif "性能" in task or "performance" in task_lower:
                result = await self._performance_analysis(task, context)
            elif "规范" in task or "lint" in task_lower:
                result = await self._check_standards(task, context)
            else:
                result = await self._general_review(task, context)
            
            self.success_count += 1
            
            return TaskResult(
                success=True,
                output=result,
                tokens_used=self.total_tokens
            )
        
        except Exception as e:
            logger.error(f"代码审查失败: {e}")
            return TaskResult(
                success=False,
                output=None,
                error=str(e)
            )
        
        finally:
            self.state = "idle"
            self.task_count += 1
    
    async def _review_code(self, code: str, context: dict) -> str:
        """代码审查"""
        prompt = f"""审查以下代码:

## 代码
```
{code}
```

## 上下文
{json.dumps(context, ensure_ascii=False, indent=2)}

## 审查要求
1. 逻辑正确性检查
2. 代码风格评估
3. 最佳实践建议
4. 潜在问题识别

## 输出格式
### 问题列表
| 严重程度 | 位置 | 问题描述 | 修复建议 |
|---------|------|---------|---------|

### 总体评分
- 代码质量: X/10
- 可维护性: X/10
- 安全性: X/10

### 改进建议
1. ...
2. ..."""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _security_audit(self, code: str, context: dict) -> str:
        """安全审计"""
        prompt = f"""对以下代码进行安全审计:

## 代码
```
{code}
```

## 审计要点
1. SQL注入风险
2. XSS攻击风险
3. 敏感数据处理
4. 权限控制
5. 输入验证
6. 加密使用

## 输出格式
### 安全问题
| 风险等级 | 类型 | 位置 | 描述 | 修复方案 |
|---------|------|------|------|---------|

### 安全评分: X/10

### 安全建议
1. ...
2. ..."""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _performance_analysis(self, code: str, context: dict) -> str:
        """性能分析"""
        prompt = f"""分析以下代码的性能:

## 代码
```
{code}
```

## 分析要点
1. 时间复杂度
2. 空间复杂度
3. I/O操作
4. 并发性能
5. 资源使用

## 输出格式
### 性能问题
| 问题类型 | 位置 | 影响 | 优化方案 |
|---------|------|------|---------|

### 性能评分: X/10

### 优化建议
1. ...
2. ..."""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _check_standards(self, code: str, context: dict) -> str:
        """规范检查"""
        language = context.get("language", "Python")
        
        prompt = f"""检查以下{language}代码的编码规范:

## 代码
```
{code}
```

## 规范标准
{"PEP8" if language == "Python" else "ESLint" if language == "JavaScript" else "通用规范"}

## 输出格式
### 规范问题
| 行号 | 规则 | 描述 | 修正建议 |
|-----|------|------|---------|

### 规范符合度: X%"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm.chat(messages, max_tokens=2000)
        self.total_tokens += response.tokens_used
        
        return response.content
    
    async def _general_review(self, task: str, context: dict) -> str:
        """通用审查"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": task}
        ]
        
        response = await self.llm.chat(messages, max_tokens=3000)
        self.total_tokens += response.tokens_used
        
        return response.content
