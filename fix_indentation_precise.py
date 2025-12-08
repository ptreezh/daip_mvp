"""
修复TUI.py文件中的缩进错误
"""
with open('src/daip_live/tui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("修复前检查错误行:")
print(f"Line 455: {lines[454]}")
print(f"Line 456: {lines[455]}")  
print(f"Line 457: {lines[456]}")
print(f"Line 458: {lines[457]}")

# 从原始代码中找到正确结构
correct_structure = """        except ImportError as e:
            print(f"⚠️  Claude Skills integration not found: {e}")
            try:
                from daip_live.skills.integration import ClaudeSkillsIntegrationService
                self._claude_integration_service = ClaudeSkillsIntegrationService(
                    skill_manager=self._skill_manager,
                    model_provider=self._model_provider
                )

                # Initialize adapter manager separately if needed
                try:
                    from daip_live.skills.claude_skill_adapter import ClaudeSkillAdapterManager
                    self._claude_skill_adapter_manager = ClaudeSkillAdapterManager(self._skill_manager)
                    print("✅ Claude Skill Adapter Manager initialized for format compatibility")
                except ImportError:
                    self._claude_skill_adapter_manager = None
                    print("⚠️  Claude Skill Adapter Manager not available")

                # Also set the integration service directly to the recognizer
                self._intent_recognizer.claude_integration_service = self._claude_integration_service
                print("✅ Claude Skills integration service connected to intent recognizer (using legacy)")
            except Exception as e:
                print(f"⚠️  Claude Skills integration service initialization failed: {e}")
                self._intent_recognizer.claude_integration_service = None
                self._claude_skill_adapter_manager = None

        except Exception as e:
"""

# 找到整个代码块的起始位置
start_line = -1
for i in range(len(lines)):
    if "except ImportError as e:" in lines[i] and i > 430 and i < 440:
        start_line = i
        break

if start_line != -1:
    print(f"\n找到起始块位置: {start_line+1}")
    
    # 找到完整的try-except块结束位置
    # 从start_line开始往后找到对应的结束
    end_line = -1
    bracket_level = 0
    for i in range(start_line, min(start_line+50, len(lines))):
        if 'try:' in lines[i] or 'try :' in lines[i]:
            bracket_level += 1
        if 'except ' in lines[i] or 'finally:' in lines[i]:
            if bracket_level > 0:
                # This except belongs to the try block we're looking for
                pass
            else:
                # This is an outer exception handler
                if end_line == -1:  # First outer exception after our block
                    end_line = i
                    break
        if 'return' in lines[i] and i > start_line+5:
            # Return statements often mark the end of try-except blocks
            end_line = i
            break

    print(f"尝试的范围: {start_line+1} 到 {end_line+1 if end_line != -1 else 'EOF'}")
    
    # 手动修复从450-470行的缩进（大概范围）
    # 查找原始代码结构
    # 在第437行左右应该有一个try-except结构
    # 需要恢复正确的缩进
    corrected_lines = lines[:]
    
    # 按行检查并修复缩进
    for i in range(445, 470):  # 修复问题区域
        if i < len(corrected_lines):
            line = corrected_lines[i]
            stripped = line.lstrip()
            
            # 修复特定的缩进问题
            if 'except ImportError as e:' in line and i == 454:
                # 第455行应该是缩进8个空格（属于外层except块的子分支）
                corrected_lines[i] = '        ' + stripped
            elif 'print(f' in line and 'adapter manager not found' in line and i == 455:
                # 第456行应该是缩进12个空格
                corrected_lines[i] = '            ' + stripped
            elif 'try:' in line and 'from daip_live.skills.integration' in line and i == 456:
                # 第457行应该是缩进12个空格
                corrected_lines[i] = '            ' + stripped
            elif 'self._claude_integration_service = ClaudeSkillsIntegrationService(' in line:
                # 第458行应该是缩进16个空格
                corrected_lines[i] = '                ' + stripped
            elif 'skill_manager=self._skill_manager,' in line:
                # 第459行应该是缩进20个空格
                corrected_lines[i] = '                    ' + stripped
            elif 'model_provider=self._model_provider' in line:
                # 第460行应该是缩进20个空格
                corrected_lines[i] = '                    ' + stripped
            elif 'self._intent_recognizer.claude_integration_service = self._claude_integration_service' in line:
                # 第468行应该是缩进16个空格
                corrected_lines[i] = '                ' + stripped
    
    print(f"修复缩进...")
    
    # 写入修复后的文件
    with open('src/daip_live/tui.py.fixed', 'w', encoding='utf-8') as f:
        f.writelines(corrected_lines)
    
    print(f"修复后的文件已保存为: src/daip_live/tui.py.fixed")
    
    # 验证修复后的语法
    import ast
    try:
        content = ''.join(corrected_lines)
        ast.parse(content)
        print("✅ 语法检查通过！")
        
        # 替换原文件
        with open('src/daip_live/tui.py', 'w', encoding='utf-8') as f:
            f.writelines(corrected_lines)
        print("✅ 原文件已更新")
        
    except SyntaxError as e:
        print(f"❌ 修复后仍有语法错误: {e}")
        print(f"错误行: {e.lineno}, 错误信息: {e.msg}")
        start = max(0, e.lineno-3)
        end = min(len(corrected_lines), e.lineno+3)
        for j in range(start, end):
            marker = '>>> ' if j == e.lineno-1 else '    '
            print(f"{marker}{j+1:4d}: {corrected_lines[j]}")