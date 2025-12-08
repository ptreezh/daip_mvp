"""
修复 TUI.py 文件中的缩进错误
"""
def fix_indentation_error():
    """修复tui.py中的缩进错误"""
    with open('src/daip_live/tui.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("修复前代码结构检查:")
    for i in range(448, 465):
        if i < len(lines):
            print(f"{i+1:4d}: {lines[i].rstrip()}")
    
    print("\n开始修复缩进错误...")
    
    # 问题出在一个 try-except 块的缩进错误。我需要分析嵌套结构
    # 看起来是第 455 行的 except 没有对应的 try 块
    
    # 重新构建正确缩进的部分
    fixed_lines = lines[:448]  # 保留之前的内容
    
    # 添加正确的代码结构
    correct_code_block = [
        "        except ImportError as e:\n",
        "            print(f\"⚠️  Claude Skills adapter manager not found: {e}\")\n",
        "            try:\n",
        "                from daip_live.skills.integration import ClaudeSkillsIntegrationService\n",
        "                self._claude_integration_service = ClaudeSkillsIntegrationService(\n",
        "                    skill_manager=self._skill_manager,\n",
        "                    model_provider=self._model_provider\n",
        "                )\n",
        "\n",
        "                # Initialize adapter manager separately if needed\n",
        "                try:\n",
        "                    from daip_live.skills.claude_skill_adapter import ClaudeSkillAdapterManager\n",
        "                    self._claude_skill_adapter_manager = ClaudeSkillAdapterManager(self._skill_manager)\n",
        "                    print(\"✅ Claude Skill Adapter Manager initialized for format compatibility\")\n",
        "                except ImportError:\n",
        "                    self._claude_skill_adapter_manager = None\n",
        "                    print(\"⚠️  Claude Skill Adapter Manager not available\")\n",
        "\n",
        "                # Also set the integration service directly to the recognizer\n",
        "                self._intent_recognizer.claude_integration_service = self._claude_integration_service\n",
        "                print(\"✅ Claude Skills integration service connected to intent recognizer (using legacy)\")\n",
        "            except Exception as e:\n",
        "                print(f\"⚠️  Claude Skills integration service initialization failed: {e}\")\n",
        "                self._intent_recognizer.claude_integration_service = None\n",
        "                self._claude_skill_adapter_manager = None\n",
        "\n",
        "        except Exception as e:\n",
        "            print(f\"⚠️  Claude Skills integration service initialization failed: {e}\")\n",
        "            self._intent_recognizer.claude_integration_service = None\n",
        "            self._claude_skill_adapter_manager = None\n"
    ]
    
    fixed_lines.extend(correct_code_block)
    
    # 添加剩余行
    fixed_lines.extend(lines[467:])
    
    print(f"\n修复后代码结构检查:")
    for i in range(448, min(475, len(fixed_lines))):
        print(f"{i+1:4d}: {fixed_lines[i].rstrip()}")
    
    # 验证修复
    print(f"\n验证Python语法...")
    code_txt = ''.join(fixed_lines)
    
    try:
        compile(code_txt, 'tui.py', 'exec')
        print("✅ 语法验证通过!")
        
        # 写入修复后的文件
        with open('src/daip_live/tui.py', 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print("✅ 文件已保存修复")
        return True
        
    except SyntaxError as e:
        print(f"❌ 修复失败，语法错误: {e}")
        print(f"  错误行: {e.lineno}, 错误: {e.msg}")
        return False


if __name__ == "__main__":
    success = fix_indentation_error()
    
    if success:
        print(f"\n🎉 TUI.py缩进错误修复完成!")
        print(f"系统现在应该能够正常运行，不会再有语法错误!")
    else:
        print(f"\n❌ 修复失败，请进一步检查语法问题!")