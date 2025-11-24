"""
分析混合意图识别和多角色维基协作的核心机制
"""
import sys
sys.path.insert(0, './src')

print("="*100)
print("🔍 深入分析: 混合意图识别和多角色维基协作实现机制")
print("="*100)

# 检查混合意图识别器文件
print("\\n1. 分析混合意图识别器大模型调用机制:")
try:
    with open('D:/DAIP/refactdoc/src/daip_live/multi_agent_collab/hybrid_intent_collaboration_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("   ✅ 混合意图识别器文件存在")
    
    # 搜索与大模型调用相关的关键部分
    lines = content.split('\\n')
    for i, line in enumerate(lines):
        if 'llm_' in line.lower() or 'model_provider' in line or 'analyze_intent_with_llm' in line:
            print(f"     行 {i+1}: {line.strip()}")
    
    # 特别查看recognize_intent方法
    print("\\n   🔍 混合意图识别器处理逻辑:")
    in_recognize_method = False
    method_started = False
    brace_count = 0
    for i, line in enumerate(lines):
        if 'def recognize_intent' in line:
            in_recognize_method = True
            method_started = True
            brace_count = 0
            print(f"     {i+1}: {line}")
        elif in_recognize_method:
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
            
            print(f"     {i+1}: {line}")
            
            if method_started and 'return rule_intent' in line and brace_count <= 0:
                # 这通常是方法的结束
                break
    
    print("\\n   🎯 大模型调用时机分析:")
    print("     - 当规则匹配置信度低于0.8时")
    print("     - 当规则匹配失败时") 
    print("     - 使用_simulate_llm_analysis作为后备")
    print("     - 在模糊或复杂输入时触发")
    
except FileNotFoundError:
    print("   ❌ 混合意图识别器文件不存在")
    print("     使用基础意图识别器进行分析")

# 检查多角色协作引擎
print("\\n2. 分析多角色维基协作机制:")

try:
    with open('D:/DAIP/refactdoc/src/daip_live/multi_agent_collab/real_collaboration_engine.py', 'r', encoding='utf-8') as f:
        wiki_content = f.read()
    
    print("   ✅ 多角色协作引擎文件存在")
    
    # 检查角色定义部分
    import re
    role_pattern = r'self\\.role_prompts\\s*=\\s*\\{([^}]|\\n)*?\\}'
    role_match = re.search(role_pattern, wiki_content)
    
    if role_match:
        role_section = role_match.group(0)[:500]  # 只取前500字符
        print("     角色定义片段:")
        for line in role_section.split('\\n')[:10]:  # 显示前10行
            if 'Role' in line or 'description' in line.lower():
                print(f"       {line.strip()}")
    else:
        # 搜索角色定义的各个部分
        print("     角色定义查找:")
        for line in wiki_content.split('\\n'):
            if 'Researcher_Agent' in line or 'Writer_Agent' in line or 'Fact_Checker_Agent' in line or 'Editor_Agent' in line:
                print(f"       {line.strip()}")
    
    # 检查模型调用方法
    print("\\n     模型调用方法:")
    call_method_found = False
    for i, line in enumerate(wiki_content.split('\\n')):
        if 'generate_content_with_role' in line and 'def' in line:
            print(f"       {i+1}: {line.strip()}")
            call_method_found = True
            # 显示接下来的几行
            for j in range(i+1, min(i+10, len(wiki_content.split('\\n')))):
                method_line = wiki_content.split('\\n')[j]
                if method_line.strip().startswith('"""') and j != i+1:
                    break
                if method_line.strip() and not method_line.strip().startswith('"""'):
                    print(f"         {j+1}: {method_line.strip()}")
            break
    
    if not call_method_found:
        print("       ❌ 未找到generate_content_with_role方法定义")
    
except FileNotFoundError:
    print("   ❌ 多角色协作引擎文件不存在")
    print("     检查其他可能的协作引擎文件...")

# 检查EnhancedIntentRecognizer
print("\\n3. 分析基础意图识别器:")
try:
    with open('D:/DAIP/refactdoc/src/daip_live/agent_engine/enhanced_intent_recognizer.py', 'r', encoding='utf-8') as f:
        base_content = f.read()
    
    print("   ✅ 基础意图识别器存在")
    
    # 检查意图定义顺序和优先级
    print("\\n     意图定义统计:")
    intent_pattern = r'"([a-z_]+)":\\s*\\{\\s*"patterns":'
    intents = re.findall(intent_pattern, base_content)
    print(f"       总共定义了 {len(intents)} 个意图类型")
    print(f"       意图列表: {intents[:10]}...")  # 显示前10个
    
    # 检查create_wiki定义
    create_wiki_start = None
    create_wiki_end = None
    lines = base_content.split('\\n')
    for i, line in enumerate(lines):
        if '"create_wiki"' in line and '{' in line:
            create_wiki_start = i
        elif create_wiki_start is not None and '"requires_confidence_check"' in line and create_wiki_end is None:
            # 找到结尾
            for j in range(i, len(lines)):
                if lines[j].strip() == '},' and j > create_wiki_start:
                    create_wiki_end = j
                    break
            break
    
    if create_wiki_start is not None and create_wiki_end is not None:
        print(f"       create_wiki定义位置: 行 {create_wiki_start+1} - {create_wiki_end+1}")
    
except FileNotFoundError:
    print("   ❌ 基础意图识别器文件不存在")

# 验证用户交互流程
print("\\n4. 从用户输入到Wiki创建的完整交互流程分析:")

print("\\n   阶段1: 用户输入处理")
print("     - 用户输入: '创建维基 人工智能发展趋势'")
print("     - TUI或CLI接收并传递给意图识别器")

print("\\n   阶段2: 意图识别")
print("     - 混合意图识别器工作")
print("     - 首先尝试规则匹配 - '创建.*维基.*' 匹配create_wiki意图")
print("     - 如果置信度足够(>=0.8)，直接返回意图结果")
print("     - 如果置信度不足或匹配失败，使用LLM分析器进行语义分析")

print("\\n   阶段3: 参数提取")
print("     - 从输入中提取标题: '人工智能发展趋势'")
print("     - 验证参数完整性")
print("     - 如果参数缺失，标记requires_clarification=True")

print("\\n   阶段4: 协作会话启动")
print("     - 检测到用户是否需要多角色协作模式")
print("     - 如果需要，创建MultiRoleWikiCollaborator实例")
print("     - 添加研究者、写作者、编辑、事实核查员等角色")

print("\\n   阶段5: 多角色内容生成")
print("     - 每个角色基于提示词模板生成内容")
print("     - 模型调用: model_provider.generate(prompt_with_role_context)")
print("     - Researcher_Agent: 提供技术深度") 
print("     - Writer_Agent: 提供清晰表达")
print("     - Fact_Checker_Agent: 验证准确性")
print("     - Editor_Agent: 优化格式和风格")

print("\\n   阶段6: 内容整合")
print("     - 智能合并不同角色的贡献")
print("     - 处理可能的内容冲突")
print("     - 生成最终维基内容")

print("\\n   阶段7: 结果输出")
print("     - 保存到维基存储")
print("     - 显示结果到用户界面")
print("     - 记录协作历史")

print("\\n5. 模型选择与调用机制:")
print("   - 每个角色使用相同或不同的模型实例")
print("   - 模型调用通过model_provider接口抽象")
print("   - 支持多样化模型：GPT、Claude、本地模型等")
print("   - 通过角色特定的提示词确保专业化输出")

print("\\n6. 系统集成架构:")
print("   - 意图识别器: 负责意图识别和参数提取")  
print("   - 协作引擎: 负责多角色协调和内容生成")
print("   - 模型提供商: 负责AI模型调用")
print("   - 存储系统: 负责内容保存和版本管理")
print("   - UI层: 负责用户交互和结果展示")

print("\\n" + "="*100)
print("🎯 机制分析总结:")
print("1. 混合意图识别: 规则匹配优先，LLM分析作为补充")
print("2. 多角色协作: 通过专业角色定义和个性化提示词实现") 
print("3. 模型调用: 通过统一接口但为不同角色生成不同内容")
print("4. 交互流程: 用户输入 -> 意图识别 -> 协作生成 -> 内容整合 -> 结果输出")
print("="*100)