"""
测试错误类型定义和分类
遵循TDD原则 - 先写测试，后写实现
"""


class TestErrorClassification:
    """测试错误分类系统"""

    def test_error_severity_enum_exists(self):
        """测试错误严重程度枚举是否存在"""
        # This test will fail until we implement ErrorSeverity
        from daip_live.cli.utils.error_types import ErrorSeverity

        # Verify enum values exist
        assert hasattr(ErrorSeverity, "LOW")
        assert hasattr(ErrorSeverity, "MEDIUM")
        assert hasattr(ErrorSeverity, "HIGH")
        assert hasattr(ErrorSeverity, "CRITICAL")

        # Verify enum values
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.CRITICAL.value == "critical"

    def test_error_category_enum_exists(self):
        """测试错误类别枚举是否存在"""
        from daip_live.cli.utils.error_types import ErrorCategory

        # Verify enum values exist
        assert hasattr(ErrorCategory, "NETWORK")
        assert hasattr(ErrorCategory, "DATABASE")
        assert hasattr(ErrorCategory, "VALIDATION")
        assert hasattr(ErrorCategory, "BUSINESS")
        assert hasattr(ErrorCategory, "SYSTEM")
        assert hasattr(ErrorCategory, "USER_INPUT")

    def test_cli_error_base_class_exists(self):
        """测试CLI错误基类是否存在"""
        from daip_live.cli.utils.error_types import CLIError

        # Test basic instantiation
        error = CLIError("Test message")

        # Verify basic attributes
        assert error.message == "Test message"
        assert error.category is not None
        assert error.severity is not None
        assert error.error_code is None
        assert error.details == {}
        assert error.original_exception is None

    def test_cli_error_with_all_parameters(self):
        """测试CLI错误完整参数构造"""
        from daip_live.cli.utils.error_types import (
            CLIError,
            ErrorCategory,
            ErrorSeverity,
        )

        original_error = ValueError("Original error")
        error = CLIError(
            message="Test error message",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            error_code="NET_001",
            details={"url": "http://example.com", "timeout": 30},
            original_exception=original_error,
        )

        assert error.message == "Test error message"
        assert error.category == ErrorCategory.NETWORK
        assert error.severity == ErrorSeverity.HIGH
        assert error.error_code == "NET_001"
        assert error.details["url"] == "http://example.com"
        assert error.details["timeout"] == 30
        assert error.original_exception == original_error

    def test_cli_error_to_dict_conversion(self):
        """测试CLI错误转换为字典格式"""
        from daip_live.cli.utils.error_types import (
            CLIError,
            ErrorCategory,
            ErrorSeverity,
        )

        error = CLIError(
            message="Test error",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.MEDIUM,
            error_code="DB_001",
            details={"table": "users", "operation": "select"},
        )

        error_dict = error.to_dict()

        assert error_dict["error_type"] == "CLIError"
        assert error_dict["message"] == "Test error"
        assert error_dict["category"] == "database"
        assert error_dict["severity"] == "medium"
        assert error_dict["error_code"] == "DB_001"
        assert error_dict["details"]["table"] == "users"
        assert error_dict["details"]["operation"] == "select"
        assert "timestamp" in error_dict

    def test_specific_error_types_exist(self):
        """测试特定错误类型是否存在"""
        from daip_live.cli.utils.error_types import (
            BusinessError,
            DatabaseError,
            NetworkError,
            SystemError,
            UserInputError,
            ValidationError,
        )

        # Test NetworkError
        network_error = NetworkError("Connection failed")
        assert network_error.category.value == "network"
        assert network_error.severity.value == "high"
        assert network_error.message == "Connection failed"

        # Test DatabaseError
        db_error = DatabaseError("Query failed")
        assert db_error.category.value == "database"
        assert db_error.severity.value == "high"

        # Test ValidationError
        validation_error = ValidationError("Invalid input")
        assert validation_error.category.value == "validation"
        assert validation_error.severity.value == "medium"

        # Test BusinessError
        business_error = BusinessError("Business rule violation")
        assert business_error.category.value == "business"

        # Test SystemError
        system_error = SystemError("System failure")
        assert system_error.category.value == "system"

        # Test UserInputError
        input_error = UserInputError("Invalid command")
        assert input_error.category.value == "user_input"

    def test_error_inheritance_hierarchy(self):
        """测试错误类型继承层次"""
        from daip_live.cli.utils.error_types import CLIError, NetworkError

        # NetworkError should inherit from CLIError
        assert issubclass(NetworkError, CLIError)

        # Test polymorphism
        error: CLIError = NetworkError("Test")
        assert isinstance(error, CLIError)
        assert isinstance(error, NetworkError)
        assert error.category.value == "network"

    def test_error_defaults(self):
        """测试错误默认值"""
        from daip_live.cli.utils.error_types import (
            ErrorCategory,
            ErrorSeverity,
            ValidationError,
        )

        error = ValidationError("Test validation")

        # Should have default category and severity
        assert error.category == ErrorCategory.VALIDATION
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.error_code is None
        assert error.details == {}
        assert error.original_exception is None


class TestErrorExamples:
    """测试错误类型的具体使用示例"""

    def test_network_error_example(self):
        """测试网络错误示例"""
        from daip_live.cli.utils.error_types import NetworkError

        # Simulate a network timeout error
        try:
            raise TimeoutError("Connection timeout after 30 seconds")
        except TimeoutError as e:
            error = NetworkError(
                message="Failed to connect to model service",
                error_code="NET_TIMEOUT",
                details={
                    "url": "https://api.example.com/models",
                    "timeout": 30,
                    "attempt": 1,
                },
                original_exception=e,
            )

            assert error.category.value == "network"
            assert error.severity.value == "high"
            assert "url" in error.details
            assert error.original_exception is not None

    def test_validation_error_example(self):
        """测试验证错误示例"""
        from daip_live.cli.utils.error_types import ValidationError

        # Simulate parameter validation error
        error = ValidationError(
            message="Invalid model type parameter",
            error_code="VALIDATION_001",
            details={
                "parameter": "type",
                "invalid_value": "invalid_type",
                "valid_values": ["all", "local", "cloud"],
                "command": "daip model list",
            },
        )

        assert error.category.value == "validation"
        assert error.severity.value == "medium"
        assert error.details["invalid_value"] == "invalid_type"

    def test_database_error_example(self):
        """测试数据库错误示例"""
        from daip_live.cli.utils.error_types import DatabaseError

        # Simulate database connection error
        try:
            raise ConnectionError("Database connection failed")
        except ConnectionError as e:
            error = DatabaseError(
                message="Failed to connect to session database",
                error_code="DB_CONNECTION",
                details={
                    "database_path": "data/daip_live.db",
                    "connection_timeout": 10,
                },
                original_exception=e,
            )

            assert error.category.value == "database"
            assert error.severity.value == "high"
            assert error.details["database_path"] == "data/daip_live.db"
