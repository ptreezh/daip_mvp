"""
测试LLM服务接口
遵循TDD原则：先写测试，再实现功能
"""

from unittest.mock import patch

import pytest

from daip_live.scaffolding.llm_service import (
    ConversationContext,
    LLMModelConfig,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    LLMService,
    LLMServiceConfig,
    MessageRole,
    PromptTemplate,
    PromptVariable,
)
from daip_live.scaffolding.models import (
    NetworkError,
    TimeoutError,
    ValidationError,
)


class TestLLMProvider:
    """测试LLM提供商枚举"""

    def test_llm_provider_values(self):
        """测试LLM提供商枚举值"""
        # TC-2.3.1: LLM提供商枚举测试
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.GOOGLE.value == "google"
        assert LLMProvider.LOCAL.value == "local"
        assert LLMProvider.OLLAMA.value == "ollama"

    def test_llm_provider_from_string(self):
        """测试从字符串获取LLM提供商"""
        # TC-2.3.2: 提供商字符串解析测试
        assert LLMProvider.from_string("openai") == LLMProvider.OPENAI
        assert LLMProvider.from_string("anthropic") == LLMProvider.ANTHROPIC
        assert LLMProvider.from_string("google") == LLMProvider.GOOGLE
        assert LLMProvider.from_string("local") == LLMProvider.LOCAL
        assert LLMProvider.from_string("ollama") == LLMProvider.OLLAMA
        assert LLMProvider.from_string("unknown") == LLMProvider.OPENAI  # 默认值


class TestMessageRole:
    """测试消息角色枚举"""

    def test_message_role_values(self):
        """测试消息角色枚举值"""
        # TC-2.3.3: 消息角色枚举测试
        assert MessageRole.SYSTEM.value == "system"
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.FUNCTION.value == "function"


class TestPromptVariable:
    """测试提示变量"""

    def test_prompt_variable_creation(self):
        """测试提示变量创建"""
        # TC-2.3.4: 提示变量创建测试
        var = PromptVariable(
            name="project_name", description="项目名称", required=True, default_value=""
        )

        assert var.name == "project_name"
        assert var.description == "项目名称"
        assert var.required
        assert var.default_value == ""

    def test_prompt_variable_validation(self):
        """测试提示变量验证"""
        # TC-2.3.5: 变量验证测试
        # 必需变量有值
        required_var = PromptVariable("test", "Test", required=True)
        assert required_var.validate("value") == []

        # 必需变量无值
        errors = required_var.validate("")
        assert len(errors) > 0
        assert any("必需" in error for error in errors)

        # 可选变量无值
        optional_var = PromptVariable("test", "Test", required=False)
        assert optional_var.validate("") == []


class TestPromptTemplate:
    """测试提示模板"""

    def test_prompt_template_creation(self):
        """测试提示模板创建"""
        # TC-2.3.6: 提示模板创建测试
        template = PromptTemplate(
            name="project_generation",
            description="项目生成提示模板",
            content="创建一个名为{project_name}的项目，描述：{description}",
            variables=[
                PromptVariable("project_name", "项目名称", required=True),
                PromptVariable("description", "项目描述", required=False),
            ],
        )

        assert template.name == "project_generation"
        assert "创建一个名为{project_name}" in template.content
        assert len(template.variables) == 2

    def test_prompt_template_render(self):
        """测试提示模板渲染"""
        # TC-2.3.7: 模板渲染测试
        template = PromptTemplate(
            name="test",
            content="Hello {name}, welcome to {project}!",
            variables=[
                PromptVariable("name", "姓名", required=True),
                PromptVariable("project", "项目", required=True),
            ],
        )

        context = {"name": "Alice", "project": "DAIP"}
        rendered = template.render(context)

        assert "Hello Alice" in rendered
        assert "welcome to DAIP" in rendered

    def test_prompt_template_missing_variable(self):
        """测试缺少变量处理"""
        # TC-2.3.8: 缺失变量测试
        template = PromptTemplate(
            name="test",
            content="Hello {name}",
            variables=[PromptVariable("name", "姓名", required=True)],
        )

        # 缺少必需变量
        with pytest.raises(ValidationError):
            template.render({})

    def test_prompt_template_default_values(self):
        """测试默认值处理"""
        # TC-2.3.9: 默认值测试
        template = PromptTemplate(
            name="test",
            content="Project: {name}, Type: {type}",
            variables=[
                PromptVariable("name", "名称", required=True),
                PromptVariable("type", "类型", required=False, default_value="web"),
            ],
        )

        rendered = template.render({"name": "MyApp"})
        assert "Project: MyApp" in rendered
        assert "Type: web" in rendered


class TestLLMModelConfig:
    """测试LLM模型配置"""

    def test_llm_model_config_creation(self):
        """测试LLM模型配置创建"""
        # TC-2.3.10: 模型配置创建测试
        config = LLMModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4",
            api_key="test_key",
            max_tokens=2000,
            temperature=0.7,
        )

        assert config.provider == LLMProvider.OPENAI
        assert config.model_name == "gpt-4"
        assert config.max_tokens == 2000
        assert config.temperature == 0.7

    def test_llm_model_config_validation(self):
        """测试LLM模型配置验证"""
        # TC-2.3.11: 配置验证测试
        # 有效配置
        config = LLMModelConfig(
            provider=LLMProvider.OPENAI, model_name="gpt-4", api_key="test_key"
        )
        errors = config.validate()
        assert len(errors) == 0

        # 无效配置 - 缺少API密钥
        invalid_config = LLMModelConfig(provider=LLMProvider.OPENAI, model_name="gpt-4")
        errors = invalid_config.validate()
        assert len(errors) > 0
        assert any("API密钥" in error for error in errors)

    def test_llm_model_config_temperature_bounds(self):
        """测试温度参数边界"""
        # TC-2.3.12: 温度边界测试
        # 有效温度
        config = LLMModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4",
            api_key="test_key",
            temperature=0.5,
        )
        errors = config.validate()
        assert len(errors) == 0

        # 无效温度 - 太低
        invalid_config = LLMModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4",
            api_key="test_key",
            temperature=-0.1,
        )
        errors = invalid_config.validate()
        assert len(errors) > 0

        # 无效温度 - 太高
        invalid_config = LLMModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4",
            api_key="test_key",
            temperature=2.1,
        )
        errors = invalid_config.validate()
        assert len(errors) > 0


class TestLLMRequest:
    """测试LLM请求"""

    def test_llm_request_creation(self):
        """测试LLM请求创建"""
        # TC-2.3.13: LLM请求创建测试
        request = LLMRequest(
            prompt="Generate a Python web application",
            context={"project_name": "MyApp"},
            max_tokens=1000,
            temperature=0.5,
        )

        assert request.prompt == "Generate a Python web application"
        assert request.context["project_name"] == "MyApp"
        assert request.max_tokens == 1000
        assert request.temperature == 0.5

    def test_llm_request_with_conversation(self):
        """测试带对话历史的请求"""
        # TC-2.3.14: 对话历史测试
        conversation = ConversationContext()
        conversation.add_message(MessageRole.USER, "Create a web app")
        conversation.add_message(MessageRole.ASSISTANT, "Sure, what kind?")

        request = LLMRequest(prompt="Make it a Flask app", conversation=conversation)

        assert len(request.conversation.messages) == 2
        assert request.conversation.messages[0].role == MessageRole.USER


class TestLLMResponse:
    """测试LLM响应"""

    def test_llm_response_creation(self):
        """测试LLM响应创建"""
        # TC-2.3.15: LLM响应创建测试
        response = LLMResponse(
            content="Here is your Flask app...",
            model="gpt-4",
            usage={"prompt_tokens": 50, "completion_tokens": 150, "total_tokens": 200},
            finish_reason="stop",
        )

        assert response.content == "Here is your Flask app..."
        assert response.model == "gpt-4"
        assert response.usage["total_tokens"] == 200
        assert response.finish_reason == "stop"

    def test_llm_response_with_error(self):
        """测试带错误的响应"""
        # TC-2.3.16: 错误响应测试
        response = LLMResponse(
            content="", error="Rate limit exceeded", error_code="rate_limit"
        )

        assert response.error == "Rate limit exceeded"
        assert response.error_code == "rate_limit"
        assert response.has_error()


class TestConversationContext:
    """测试对话上下文"""

    def test_conversation_context_creation(self):
        """测试对话上下文创建"""
        # TC-2.3.17: 对话上下文创建测试
        context = ConversationContext(max_messages=10)

        assert context.max_messages == 10
        assert len(context.messages) == 0

    def test_conversation_add_message(self):
        """测试添加消息"""
        # TC-2.3.18: 添加消息测试
        context = ConversationContext()
        context.add_message(MessageRole.USER, "Hello")
        context.add_message(MessageRole.ASSISTANT, "Hi there!")

        assert len(context.messages) == 2
        assert context.messages[0].content == "Hello"
        assert context.messages[1].content == "Hi there!"

    def test_conversation_context_limit(self):
        """测试消息数量限制"""
        # TC-2.3.19: 消息限制测试
        context = ConversationContext(max_messages=2)

        context.add_message(MessageRole.USER, "Message 1")
        context.add_message(MessageRole.USER, "Message 2")
        context.add_message(MessageRole.USER, "Message 3")  # 应该移除第一条

        assert len(context.messages) == 2
        assert context.messages[0].content == "Message 2"
        assert context.messages[1].content == "Message 3"

    def test_conversation_clear(self):
        """测试清空对话"""
        # TC-2.3.20: 清空对话测试
        context = ConversationContext()
        context.add_message(MessageRole.USER, "Test")
        assert len(context.messages) == 1

        context.clear()
        assert len(context.messages) == 0


class TestLLMServiceConfig:
    """测试LLM服务配置"""

    def test_llm_service_config_creation(self):
        """测试LLM服务配置创建"""
        # TC-2.3.21: 服务配置创建测试
        model_config = LLMModelConfig(
            provider=LLMProvider.OPENAI, model_name="gpt-4", api_key="test_key"
        )

        service_config = LLMServiceConfig(
            default_model=model_config, timeout=30.0, max_retries=3
        )

        assert service_config.default_model == model_config
        assert service_config.timeout == 30.0
        assert service_config.max_retries == 3

    def test_llm_service_config_add_model(self):
        """测试添加模型配置"""
        # TC-2.3.22: 添加模型测试
        service_config = LLMServiceConfig()

        model_config = LLMModelConfig(
            provider=LLMProvider.OPENAI, model_name="gpt-3.5-turbo", api_key="test_key"
        )

        service_config.add_model("gpt-3.5-turbo", model_config)
        assert "gpt-3.5-turbo" in service_config.models
        assert service_config.models["gpt-3.5-turbo"] == model_config


class TestLLMService:
    """测试LLM服务"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.model_config = LLMModelConfig(
            provider=LLMProvider.OPENAI, model_name="gpt-4", api_key="test_key"
        )
        self.service_config = LLMServiceConfig(default_model=self.model_config)
        self.llm_service = LLMService(config=self.service_config)

    def test_llm_service_creation(self):
        """测试LLM服务创建"""
        # TC-2.3.23: 服务创建测试
        service = LLMService()
        assert service.config is not None
        assert service.default_provider == LLMProvider.OPENAI

    def test_llm_service_with_config(self):
        """测试使用自定义配置创建服务"""
        # TC-2.3.24: 自定义配置服务测试
        service = LLMService(config=self.service_config)
        assert service.config == self.service_config
        assert service.default_provider == LLMProvider.OPENAI

    @pytest.mark.asyncio
    async def test_generate_text_success(self):
        """测试成功生成文本"""
        # TC-2.3.25: 文本生成成功测试
        request = LLMRequest(prompt="Generate a simple Python function")

        # Mock成功响应
        mock_response = LLMResponse(
            content="def hello():\n    print('Hello, World!')",
            model="gpt-4",
            usage={"total_tokens": 50},
        )

        with patch.object(
            self.llm_service, "_call_provider", return_value=mock_response
        ):
            response = await self.llm_service.generate_text(request)

            assert response.success
            assert "def hello():" in response.content
            assert response.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_generate_text_with_context(self):
        """测试带上下文生成文本"""
        # TC-2.3.26: 上下文生成测试
        context = {"project_name": "MyApp", "language": "Python"}
        request = LLMRequest(
            prompt="Create a main function for {project_name}", context=context
        )

        mock_response = LLMResponse(
            content="def main():\n    print('Hello from MyApp!')", model="gpt-4"
        )

        with patch.object(
            self.llm_service, "_call_provider", return_value=mock_response
        ):
            response = await self.llm_service.generate_text(request)

            assert response.success
            assert "MyApp" in response.content

    @pytest.mark.asyncio
    async def test_generate_text_with_conversation(self):
        """测试带对话历史生成文本"""
        # TC-2.3.27: 对话生成测试
        conversation = ConversationContext()
        conversation.add_message(MessageRole.USER, "Create a web app")
        conversation.add_message(MessageRole.ASSISTANT, "Sure, Flask or Django?")

        request = LLMRequest(prompt="Flask", conversation=conversation)

        mock_response = LLMResponse(content="Here's a Flask app...", model="gpt-4")

        with patch.object(
            self.llm_service, "_call_provider", return_value=mock_response
        ):
            response = await self.llm_service.generate_text(request)

            assert response.success
            assert len(request.conversation.messages) == 2  # 验证对话历史被保留

    @pytest.mark.asyncio
    async def test_generate_text_network_error(self):
        """测试网络错误处理"""
        # TC-2.3.28: 网络错误测试
        request = LLMRequest(prompt="Test")

        with patch.object(
            self.llm_service,
            "_call_provider",
            side_effect=NetworkError("Connection failed"),
        ):
            response = await self.llm_service.generate_text(request)

            assert not response.success
            assert "Connection failed" in response.error
            assert response.error_code == "network_error"

    @pytest.mark.asyncio
    async def test_generate_text_timeout_error(self):
        """测试超时错误处理"""
        # TC-2.3.29: 超时错误测试
        request = LLMRequest(prompt="Test")

        with patch.object(
            self.llm_service,
            "_call_provider",
            side_effect=TimeoutError("Request timeout"),
        ):
            response = await self.llm_service.generate_text(request)

            assert not response.success
            assert "Request timeout" in response.error
            assert response.error_code == "timeout_error"

    @pytest.mark.asyncio
    async def test_generate_text_with_retry(self):
        """测试重试机制"""
        # TC-2.3.30: 重试机制测试
        request = LLMRequest(prompt="Test")

        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("Temporary failure")
            return LLMResponse(content="Success after retry", model="gpt-4")

        with patch.object(self.llm_service, "_call_provider", side_effect=mock_call):
            response = await self.llm_service.generate_text(request)

            assert response.success
            assert response.content == "Success after retry"
            assert call_count == 3  # 验证重试次数

    @pytest.mark.asyncio
    async def test_generate_text_rate_limit(self):
        """测试速率限制处理"""
        # TC-2.3.31: 速率限制测试
        request = LLMRequest(prompt="Test")

        rate_limit_response = LLMResponse(
            content="", error="Rate limit exceeded", error_code="rate_limit"
        )

        with patch.object(
            self.llm_service, "_call_provider", return_value=rate_limit_response
        ):
            response = await self.llm_service.generate_text(request)

            assert not response.success
            assert response.error_code == "rate_limit"

    @pytest.mark.asyncio
    async def test_generate_text_with_custom_model(self):
        """测试使用自定义模型"""
        # TC-2.3.32: 自定义模型测试
        custom_model = LLMModelConfig(
            provider=LLMProvider.ANTHROPIC, model_name="claude-3", api_key="test_key"
        )

        request = LLMRequest(prompt="Test", model_config=custom_model)

        mock_response = LLMResponse(content="Claude response", model="claude-3")

        with patch.object(
            self.llm_service, "_call_provider", return_value=mock_response
        ):
            response = await self.llm_service.generate_text(request)

            assert response.success
            assert response.model == "claude-3"

    def test_add_prompt_template(self):
        """测试添加提示模板"""
        # TC-2.3.33: 添加模板测试
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}",
            variables=[PromptVariable("name", "姓名", required=True)],
        )

        self.llm_service.add_prompt_template(template)
        assert "test_template" in self.llm_service.prompt_templates
        assert self.llm_service.prompt_templates["test_template"] == template

    def test_use_prompt_template(self):
        """测试使用提示模板"""
        # TC-2.3.34: 使用模板测试
        template = PromptTemplate(
            name="project_template",
            content="Create a {language} project named {project_name}",
            variables=[
                PromptVariable("language", "语言", required=True),
                PromptVariable("project_name", "项目名", required=True),
            ],
        )

        self.llm_service.add_prompt_template(template)

        rendered = self.llm_service.use_prompt_template(
            "project_template", {"language": "Python", "project_name": "MyApp"}
        )

        assert "Python project" in rendered
        assert "MyApp" in rendered

    @pytest.mark.asyncio
    async def test_generate_from_template(self):
        """测试从模板生成"""
        # TC-2.3.35: 模板生成测试
        template = PromptTemplate(
            name="code_generation",
            content="Generate {language} code for {description}",
            variables=[
                PromptVariable("language", "语言", required=True),
                PromptVariable("description", "描述", required=True),
            ],
        )

        self.llm_service.add_prompt_template(template)

        mock_response = LLMResponse(content="def hello():\n    pass", model="gpt-4")

        with patch.object(
            self.llm_service, "_call_provider", return_value=mock_response
        ):
            response = await self.llm_service.generate_from_template(
                "code_generation",
                {"language": "Python", "description": "hello function"},
            )

            assert response.success
            assert "def hello()" in response.content

    @pytest.mark.asyncio
    async def test_streaming_generation(self):
        """测试流式生成"""
        # TC-2.3.36: 流式生成测试
        request = LLMRequest(prompt="Generate a Python function", stream=True)

        # Mock流式响应
        async def mock_stream(*args, **kwargs):
            chunks = ["def", " hello", "():", " pass"]
            for chunk in chunks:
                yield LLMResponse(content=chunk, finished=False)
            yield LLMResponse(content="", finished=True)

        with patch.object(
            self.llm_service, "_call_provider_stream", side_effect=mock_stream
        ):
            responses = []
            async for response in self.llm_service.generate_text_stream(request):
                responses.append(response)

            assert len(responses) == 5
            assert responses[-1].finished
            assert "".join(r.content for r in responses[:-1]) == "def hello(): pass"

    def test_model_validation(self):
        """测试模型验证"""
        # TC-2.3.37: 模型验证测试
        # 有效模型
        valid_config = LLMModelConfig(
            provider=LLMProvider.OPENAI, model_name="gpt-4", api_key="test_key"
        )
        errors = self.llm_service.validate_model_config(valid_config)
        assert len(errors) == 0

        # 无效模型
        invalid_config = LLMModelConfig(
            provider=LLMProvider.OPENAI, model_name="", api_key="test_key"
        )
        errors = self.llm_service.validate_model_config(invalid_config)
        assert len(errors) > 0

    @pytest.mark.asyncio
    async def test_provider_fallback(self):
        """测试提供商回退"""
        # TC-2.3.38: 提供商回退测试
        # 配置回退提供商
        fallback_model = LLMModelConfig(
            provider=LLMProvider.LOCAL, model_name="local-model"
        )
        self.service_config.fallback_model = fallback_model

        request = LLMRequest(prompt="Test")

        # Mock _call_provider 方法，使其在调用LOCAL提供商时成功
        def mock_call_provider(provider, request):
            if provider == LLMProvider.LOCAL:
                return LLMResponse(content="Fallback response", model="local-model")
            else:
                raise NetworkError("OpenAI down")

        with patch.object(
            self.llm_service, "_call_provider", side_effect=mock_call_provider
        ):
            response = await self.llm_service.generate_text(request)

            assert response.success
            assert response.content == "Fallback response"
            assert response.model == "local-model"


if __name__ == "__main__":
    # Run tests when this file is executed directly
    pytest.main([__file__, "-v"])
