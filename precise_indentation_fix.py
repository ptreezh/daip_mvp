"""
精准修复tui.py中的缩进错误
"""
def analyze_and_fix_indentation():
    with open('src/daip_live/tui.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 分析缩进结构...")
    
    # 查找错误位置周围的缩进结构
    print("问题区域代码:")
    for i in range(445, min(475, len(lines))):
        content = lines[i].rstrip()
        indent_spaces = len(lines[i]) - len(lines[i].lstrip()) if lines[i].strip() else 0
        print(f"{i+1:4d}: {indent_spaces:2d}sp | {repr(content)}")
    
    # 检查具体问题 - 我们需要理解正确的try-except嵌套结构
    print("\n🔍 修复缩进错误...")
    
    # 查找完整的上下文以确定正确的缩进
    # 找到包含Claude Skills处理的完整代码块
    import re
    
    # 找到错误行的准确位置
    error_line_idx = 454  # Python索引，对应第455行
    print(f"错误发生在 lines[{error_line_idx}] 即第{error_line_idx+1}行")
    
    # 这里有个关键问题：我需要找到正确的缩进结构
    # 第455行 (lines[454]) 应该是 'except ImportError as e:'
    # 这行应该与第439行的 try 块对应
    
    # 让我检查实际的上下文来找到正确的结构
    fixed_lines = []
    
    # 复制到错误行之前的部分
    fixed_lines.extend(lines[:454])
    
    # 修复从第455行开始的问题
    # 从原始代码逻辑来看，应该是：
    original_problematic_section = [
        '        except ImportError as e:\\n',  # Line 455
        '            print(f"⚠️  Claude Skills adapter manager not found: {e}")\\n',  # Line 456
        '            try:\\n',  # Line 457
        '                from daip_live.skills.integration import ClaudeSkillsIntegrationService\\n',  # Line 458
        '                self._claude_integration_service = ClaudeSkillsIntegrationService(\\n',  # Line 459
        '                    skill_manager=self._skill_manager,\\n',  # Line 460
        '                    model_provider=self._model_provider\\n',  # Line 461
        '                )\\n',  # Line 462
        '\\n',  # Line 463
        '                # Initialize adapter manager separately if needed\\n',  # Line 464
        '                try:\\n',  # Line 465
        '                    from daip_live.skills.claude_skill_adapter import ClaudeSkillAdapterManager\\n',  # Line 466
        '                    self._claude_skill_adapter_manager = ClaudeSkillAdapterManager(self._skill_manager)\\n',  # Line 467
        '                    print("✅ Claude Skill Adapter Manager initialized for format compatibility")\\n',  # Line 468
        '                except ImportError:\\n',  # Line 469
        '                    self._claude_skill_adapter_manager = None\\n',  # Line 470
        '                    print("⚠️  Claude Skill Adapter Manager not available")\\n',  # Line 471
        '\\n',  # Line 472
        '                # Also set the integration service directly to the recognizer\\n',  # Line 473
        '                self._intent_recognizer.claude_integration_service = self._claude_integration_service\\n',  # Line 474
        '                print("✅ Claude Skills integration service connected to intent recognizer (using legacy)")\\n',  # Line 475
        '            except Exception as e:\\n',  # Line 476
        '                print(f"⚠️  Claude Skills integration service initialization failed: {e}")\\n',  # Line 477
        '                self._intent_recognizer.claude_integration_service = None\\n',  # Line 478
        '                self._claude_skill_adapter_manager = None\\n',  # Line 479
        '        except Exception as e:\\n',  # Line 480
        '            print(f"⚠️  Claude Skills integration service initialization failed: {e}")\\n',  # Line 481
        '            self._intent_recognizer.claude_integration_service = None\\n',  # Line 482
        '            self._claude_skill_adapter_manager = None\\n',  # Line 483
    ]
    
    # 确定正确的缩进
    correct_section = [
        '        except ImportError as e:\n',  # 缩进8个空格 - 对应外部try
        '            print(f"⚠️  Claude Skills adapter manager not found: {e}")\n',  # 缩进12个空格
        '            try:\n',  # 缩进12个空格
        '                from daip_live.skills.integration import ClaudeSkillsIntegrationService\n',  # 缩进16个空格
        '                self._claude_integration_service = ClaudeSkillsIntegrationService(\n',  # 缩进16个空格
        '                    skill_manager=self._skill_manager,\n',  # 缩进20个空格
        '                    model_provider=self._model_provider\n',  # 缩进20个空格
        '                )\n',  # 缩进16个空格
        '\n',  # 缩进16个空格 (空行保持缩进)
        '                # Initialize adapter manager separately if needed\n',  # 缩进16个空格
        '                try:\n',  # 缩进16个空格
        '                    from daip_live.skills.claude_skill_adapter import ClaudeSkillAdapterManager\n',  # 缩进20个空格
        '                    self._claude_skill_adapter_manager = ClaudeSkillAdapterManager(self._skill_manager)\n',  # 缩进20个空格
        '                    print("✅ Claude Skill Adapter Manager initialized for format compatibility")\n',  # 缩进20个空格
        '                except ImportError:\n',  # 缩进16个空格
        '                    self._claude_skill_adapter_manager = None\n',  # 缩进20个空格
        '                    print("⚠️  Claude Skill Adapter Manager not available")\n',  # 缩进20个空格
        '\n',  # 缩进16个空格
        '                # Also set the integration service directly to the recognizer\n',  # 缩进16个空格
        '                self._intent_recognizer.claude_integration_service = self._claude_integration_service\n',  # 缩进16个空格
        '                print("✅ Claude Skills integration service connected to intent recognizer (using legacy)")\n',  # 缩进16个空格
        '            except Exception as e:\n',  # 缩进12个空格
        '                print(f"⚠️  Claude Skills integration service initialization failed: {e}")\n',  # 缩进16个空格
        '                self._intent_recognizer.claude_integration_service = None\n',  # 缩进16个空格
        '                self._claude_skill_adapter_manager = None\n',  # 缩进16个空格
        '        except Exception as e:\n',  # 缩进8个空格
        '            print(f"⚠️  Claude Skills integration service initialization failed: {e}")\n',  # 缩进12个空格
        '            self._intent_recognizer.claude_integration_service = None\n',  # 缩进12个空格
        '            self._claude_skill_adapter_manager = None\n',  # 缩进12个空格
    ]
    
    # 添加修复后的结构
    fixed_lines.extend(correct_section)
    
    # 添加其余部分
    if len(lines) > 483:
        fixed_lines.extend(lines[483:])
    
    print(f"✅ 应用缩进修复...")
    
    # 验证修复后语法
    import ast
    try:
        content = ''.join(fixed_lines)
        ast.parse(content)
        print("✅ 语法检查通过！")
        
        # 保存修复后的文件
        with open('src/daip_live/tui.py', 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        print("✅ 已保存修复后的文件")
        
        return True
    except SyntaxError as e:
        print(f"❌ 修复后仍有语法错误: {e}")
        print(f"  行号: {e.lineno}")
        print(f"  信息: {e.msg}")
        return False


if __name__ == "__main__":
    success = analyze_and_fix_indentation()
    
    if success:
        print(f"\n✅ 缩进错误已成功修复！")
        print(f"现在文件应该可以通过Python语法检查了。")
    else:
        print(f"\n❌ 缩进修复失败。")