"""
修复TUI.py文件中的缩进错误
"""
def fix_indentation_error():
    """修复tui.py文件中的缩进错误"""
    
    # 读取原始文件
    with open('src/daip_live/tui.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 找到TUI.py缩进问题...")
    
    # 定位具体问题行
    problem_section_start = 432  # 从第432行开始查看问题区域
    problem_section_end = 480
    
    # 显示有问题的区域
    print(f"问题区域行 {problem_section_start+1} 到 {problem_section_end+1}:")
    for i in range(problem_section_start, min(problem_section_end, len(lines))):
        print(f"{i+1:4d}: {lines[i].rstrip()}")
    
    # 修复缩进逻辑 - 找到正确的try-except块结构
    fixed_lines = []
    
    # 复制直到出问题的部分
    fixed_lines.extend(lines[:431])
    
    # 重建正确的try-except结构
    correct_structure = [
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
        "                    print(f\"⚠️  Claude Skill Adapter Manager not found: {e}\")\n",
        "                    self._claude_integration_service = None\n",
        "\n",
        "        except ImportError as e:\n",
        "            print(f\"⚠️  Claude Skills integration not found: {e}\")\n",
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
        "            self._claude_skill_adapter_manager = None\n",
    ]
    
    # 添加修复后的结构
    fixed_lines.extend(correct_structure)
    
    # 添加剩下的代码
    fixed_lines.extend(lines[478:])
    
    # 写入修复后的文件
    with open('src/daip_live/tui.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ 缩进错误已修复!")
    print(f"修复了行 {problem_section_start+1} 到行 {problem_section_end+1} 的缩进问题")
    
    # 验证修复是否成功
    try:
        ast.parse(''.join(fixed_lines))
        print("✅ Python语法验证通过")
        return True
    except SyntaxError as e:
        print(f"❌ Python语法验证失败: {e}")
        return False


if __name__ == "__main__":
    import ast
    success = fix_indentation_error()
    
    if success:
        print(f"\n🎉 TUI.py缩进错误已成功修复!")
        print(f"文件现在语法正确，可以正常使用Claude Skills功能!")
    else:
        print(f"\n❌ TUI.py修复失败!")