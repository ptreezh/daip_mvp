# CLI Intent Recognition Integration Test Task

- [x] 创建一个测试文件 tests/integration/test_cli_intent_recognition.py，用于测试CLI中意图识别功能的集成。测试应验证：
1. CLI命令行参数能正确传递给意图识别器
2. 识别出的意图能正确转换为相应的命令执行
3. 不同类型的意图（debate、wiki、project等）都能正确处理
4. 无法识别的意图能给出适当反馈

请使用pytest框架编写测试，确保测试覆盖各种自然语言输入场景。