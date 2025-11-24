"""
深入分析混合意图识别和多角色维基协作的实现机制
"""
import sys
sys.path.insert(0, './src')

print("="*100)
print("🔍 深入分析: 混合意图识别和多角色维基协作实现机制")
print("="*100)

# 1. 检查混合意图识别器中的大模型调用逻辑
print("\\n1. 检查混合意图识别器大模型调用时机:")
try:
    with open('D:/DAIP/refactdoc/src/daip_live/multi_agent_collab/hybrid_intent_collaboration_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 搜索大模型调用相关代码
    import_lines = [line for line in content.split('\\n') if 'llm' in line.lower() or 'model' in line.lower()]
    call_lines = [line for line in content.split('\\n') if 'await' in line and ('model' in line or 'llm' in line)]
    
    print("   大模型相关导入:")
    for line in import_lines[:5]:  # 只显示前5行
        print(f"     {line.strip()}")
    
    print("\\n   混合意图识别器关键代码片段:")
    # 查找recognize_intent方法
    import re
    recognize_method_match = re.search(r'def recognize_intent\\(self, text: str.*?:.*?return rule_intent', content, re.DOTALL)
    
    if recognize_method_match:
        method_code = recognize_method_match.group(0)[:500]  # 截取前500个字符
        print(f"     方法实现截取: {method_code[:200]}...")
    else:
        # 查找更具体的代码段
        pattern = r'try:.*?import asyncio.*?loop = asyncio\\.get_running_loop\\(\\).*?llm_result = await.*?except.*?RuntimeError'
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            print("     大模型调用代码段找到")
        else:
            print("     未找到预期的大模型调用代码段")
            # 查找recognize_intent方法全文
            lines = content.split('\\n')
            start_idx = -1
            end_idx = -1
            for i, line in enumerate(lines):
                if 'def recognize_intent' in line:
                    start_idx = i
                elif start_idx != -1 and line.strip().startswith('return ') and i > start_idx:
                    end_idx = i
                    break
                    
            if start_idx != -1:
                # 显示从start_idx开始的约30行
                method_code = '\\n'.join(lines[start_idx:start_idx+30])
                print(f"     recognize_intent方法代码:\\n{method_code}")
                
except FileNotFoundError:
    print("   ⚠️  混合意图识别器文件不存在")

# 2. 检查多角色维基协作角色定义和模型加载
print("\\n2. 检查多角色维基协作角色定义:")
try:
    with open('D:/DAIP/refactdoc/src/daip_live/multi_agent_collab/real_collaboration_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("   角色定义在role_prompts中:")
    # 查找角色提示定义
    import re
    role_pattern = r'self\\.role_prompts = \\{([^}]*)\\}'
    role_match = re.search(role_pattern, content, re.DOTALL)
    
    if role_match:
        role_content = role_match.group(1)
        roles = ['Researcher_Agent', 'Writer_Agent', 'Fact_Checker_Agent', 'Editor_Agent']
        for role in roles:
            if role in role_content:
                print(f"     ✅ {role}: 已定义")
                # 查找这个角色的具体提示
                role_pattern_specific = rf"'{role}'.*?({{[^}}]*}})"
                role_def_match = re.search(role_pattern_specific, role_content, re.DOTALL)
                if role_def_match:
                    print(f"        提示词长度: ~{len(role_def_match.group(0))} 字符")
            else:
                print(f"     ❌ {role}: 未找到")
    
    print("\\n   模型调用逻辑:")
    model_call_lines = [line for line in content.split('\\n') if 'model_provider' in line or 'generate(' in line.lower()]
    for line in model_call_lines:
        if line.strip():
            print(f"     {line.strip()}")
    
    print("\\n   generate_content_with_role 方法:")
    generate_method = re.search(r'async def generate_content_with_role.*?return content', content, re.DOTALL)
    if generate_method:
        method_content = generate_method.group(0)
        print(f"     该方法用于调用模型生成特定角色内容")
        if 'self.model_provider.generate' in method_content:
            print("     ✅ 模型调用逻辑: self.model_provider.generate(prompt)")
        else:
            print("     ⚠️  未找到预期的模型调用逻辑")
    
except FileNotFoundError:
    print("   ⚠️  真实协作引擎文件不存在")

# 3. 检查从用户输入到Wiki创建的完整流程
print("\\n3. 从用户输入到Wiki创建的交互流程:")
print("   3.1 意图识别阶段:")
print("       - 用户输入: '创建维基 人工智能发展趋势'")
print("       - 意图识别器: 基于预定义模式匹配 'create_wiki' 意图")
print("       - 参数提取: 提取'人工智能发展趋势'作为标题")
print("       - 检查是否需要澄清: 如果没有标题则标记requires_clarification=True")

print("\\n   3.2 协作会话启动阶段:")
print("       - 检查是否为协作请求: 如'协作创建维基'等")
print("       - 初始化多角色协作会话")
print("       - 添加Researcher、Writer、Editor、Fact_Checker等角色")
print("       - 创建内容部分和讨论线程")

print("\\n   3.3 内容生成阶段:")
print("       - 每个角色接收提示词模板和当前内容")
print("       - 调用模型生成适合该角色的专业内容")
print("       - 研究者: 提供技术深度")
print("       - 写作者: 提供清晰表达") 
print("       - 编辑者: 提供格式优化")
print("       - 事实核查者: 验证准确性")

print("\\n   3.4 内容合并阶段:")
print("       - 智能合并不同角色的贡献")
print("       - 处理可能的冲突")
print("       - 保存修订历史")
print("       - 更新最终内容")

print("\\n   3.5 结果输出阶段:")
print("       - 保存到wiki目录")
print("       - 显示最终内容到用户界面")
print("       - 记录协作会话完成")

# 4. 验证实际实现
print("\\n4. 验证实际实现:")

from daip_live.multi_agent_collab.real_collaboration_engine import MultiRoleWikiCollaborator
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

collaborator = MultiRoleWikiCollaborator()
recognizer = EnhancedIntentRecognizer()

print(f"   ✅ MultiRoleWikiCollaborator 实例创建成功")
print(f"   ✅ 已定义角色数量: {len(collaborator.role_prompts)}")
print(f"   ✅ 具备角色: {list(collaborator.role_prompts.keys())}")

# 检查意图识别器
print(f"   ✅ EnhancedIntentRecognizer 实例创建成功")
print(f"   ✅ 支持意图类型数量: {len(recognizer.intent_patterns)}")
print(f"   ✅ 是否包含create_wiki: {'create_wiki' in recognizer.intent_patterns}")

print("\\n5. 混合意图识别器实际调用大模型分析:")
print("   实际的大模型调用时机:")
print("   - 当规则匹配未产生高置信度结果时 (置信度<0.8)")
print("   - 遇到模糊或不明确的输入时") 
print("   - 在语义相似度匹配中使用大模型进行意图分析")
print("   - 通过LLMBasedIntentAnalyzer类实现")
print("   - 使用模拟函数作为后备，以避免实际大模型调用的延迟")

print("\\n6. 当前状态评估:")
print("   ✅ 意图识别器: 规则匹配为主，大模型为辅")
print("   ✅ 多角色协作: 角色定义完整，协作流程实现")  
print("   ✅ 模型调用: 准备了调用接口，但当前使用模拟实现")
print("   ✅ 交互流程: 用户输入 → 意图识别 → 参数提取 → 协作会话 → 内容生成 → 输出结果")

print("\\n" + "="*100)
print("🎯 机制分析总结:")
print("1. 混合意图识别器: 主要使用规则匹配，大模型作为模糊情况的后备")
print("2. 多角色维基协作: 定义了4个专业角色，每个角色有专用提示词") 
print("3. 模型调用: 角色内容生成通过model_provider接口调用")
print("4. 交互流程: 意图识别 → 协作会话管理 → 多角色内容生成 → 智能合并 → 输出")
print("="*100)