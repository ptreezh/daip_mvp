# DAIP-LIVE 开发记忆库

**最后更新**: 2025-08-19  
**维护者**: DAIP-LIVE 开发团队

## 🚀 **重要命令**

### **测试命令**
```bash
# 运行制度原语测试
python -m pytest tests/institutional_primitives/test_debate_rule_primitive.py -v

# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试类
python -m pytest tests/institutional_primitives/test_debate_rule_primitive.py::TestDebateRulePrimitive -v
```

### **代码质量检查**
```bash
# 使用 ruff 进行代码检查
ruff check src/
ruff format src/

# 运行类型检查 (如果配置了 mypy)
mypy src/
```

### **开发工具**
```bash
# 运行调试脚本
python debug_debate_rule.py

# 查看项目结构
tree src/ -I "__pycache__"
```

## 📋 **开发流程**

### **TDD 开发流程**
1. **RED 阶段**: 编写失败的测试
2. **GREEN 阶段**: 实现最简单的代码让测试通过
3. **REFACTOR 阶段**: 重构代码，提高质量

### **代码规范**
- **Python 3.12+**: 使用现代 Python 特性
- **Pydantic v2**: 使用 `model_dump()` 而不是 `dict()`
- **类型提示**: 完整的类型注解
- **异步编程**: 使用 `async/await`
- **错误处理**: 全面的异常处理

## 🏗️ **架构模式**

### **制度原语 (Institutional Primitives)**
```python
# 基础结构
class InstitutionalPrimitive(ABC):
    @abstractmethod
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        pass
    
    @abstractmethod
    def get_input_schema(self) -> dict[str, Any]:
        pass
    
    @abstractmethod
    def get_output_schema(self) -> dict[str, Any]:
        pass
```

### **配置模式**
```python
# 使用 Pydantic 进行配置管理
class DebateRuleConfiguration(BaseModel):
    rule_id: str
    rule_type: DebateRuleType
    max_participants: int = Field(ge=1, default=10)
    
    @field_validator('max_participants')
    @classmethod
    def validate_max_participants(cls, v):
        if v < 1:
            raise ValueError('Max participants must be at least 1')
        return v
```

### **测试模式**
```python
# 使用 pytest 和异步测试
@pytest.mark.asyncio
async def test_debate_rule_execution():
    # Arrange
    config = DebateRuleConfiguration(...)
    primitive = DebateRulePrimitive("test", config.model_dump())
    
    # Act
    result = await primitive.execute(inputs, context)
    
    # Assert
    assert result["validation_result"]["is_valid"] is True
```

## 🔧 **常用工具和库**

### **核心依赖**
- **FastAPI**: Web 框架
- **Typer**: CLI 框架
- **Pydantic**: 数据验证
- **Pytest**: 测试框架
- **Rich**: 终端格式化

### **开发工具**
- **Ruff**: 代码检查和格式化
- **MyPy**: 类型检查
- **Pre-commit**: Git hooks
- **Git**: 版本控制

## 📁 **项目结构**

```
src/
├── institutional_primitives/     # 制度原语系统
│   ├── base.py                   # 基础类定义
│   ├── debate_rule_primitive.py  # 辩论规则原语
│   ├── primitives.py             # 基础原语实现
│   └── consensus_customization.py # 共识机制
├── cli/                         # CLI 命令
│   ├── commands/                # 命令实现
│   └── main.py                  # CLI 入口
├── api/                         # API 接口
└── core_services/               # 核心服务

tests/
├── institutional_primitives/    # 制度原语测试
├── cli/                        # CLI 测试
└── integration/                # 集成测试
```

## 🎯 **最佳实践**

### **代码组织**
- 每个模块都有明确的职责
- 使用抽象基类定义接口
- 配置与逻辑分离
- 依赖注入模式

### **测试策略**
- 测试驱动开发 (TDD)
- 单元测试覆盖核心逻辑
- 集成测试验证组件协作
- 边界条件测试

### **错误处理**
- 使用自定义异常类型
- 提供有意义的错误信息
- 记录详细的错误日志
- 优雅的错误恢复

### **性能优化**
- 异步 I/O 操作
- 缓存频繁访问的数据
- 避免不必要的计算
- 使用性能分析工具

## 📚 **文档规范**

### **代码文档**
- 使用 Google 风格的文档字符串
- 提供参数和返回值说明
- 包含使用示例
- 记录已知限制

### **API 文档**
- 使用 OpenAPI 规范
- 提供请求/响应示例
- 包含错误码说明
- 版本兼容性信息

### **用户文档**
- 清晰的安装指南
- 详细的使用说明
- 常见问题解答
- 故障排除指南

## 🔍 **调试技巧**

### **日志记录**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Processing request")
logger.error(f"Error occurred: {e}")
```

### **调试输出**
```python
# 使用 print 进行简单调试
print(f"Debug: {variable}")

# 使用 pdb 进行交互式调试
import pdb; pdb.set_trace()
```

### **性能分析**
```python
import time
start_time = time.time()
# ... 执行代码 ...
end_time = time.time()
print(f"Execution time: {end_time - start_time:.3f}s")
```

## 🚨 **常见问题**

### **导入错误**
- 确保模块路径正确
- 检查 `__init__.py` 文件
- 验证 Python 路径设置

### **异步问题**
- 使用 `async/await` 语法
- 确保事件循环正确运行
- 避免阻塞操作

### **配置问题**
- 验证配置文件格式
- 检查必需的配置项
- 使用默认值处理可选配置

## 📈 **性能基准**

### **响应时间**
- API 请求: < 100ms
- 数据库查询: < 50ms
- 文件操作: < 200ms

### **资源使用**
- 内存使用: < 512MB
- CPU 使用: < 50%
- 并发处理: 1000+ 请求/秒

### **测试覆盖率**
- 单元测试: > 90%
- 集成测试: > 80%
- 端到端测试: > 70%

---

**注意**: 这是一个活跃的开发文档，请随着项目进展定期更新。