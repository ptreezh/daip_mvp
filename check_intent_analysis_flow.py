"""
检查混合意图识别流程的真实实现
"""
import sys
sys.path.insert(0, './src')

print("🔍 检查混合意图识别流程...")

# 1. 检查是否真的实现了LLM意图分析器
try:
    from daip_live.multi_agent_collab.real_collaboration_engine import LLMBasedIntentAnalyzer
    print("✅ LLM意图分析器类存在")
    
    # 尝试创建实例
    analyzer = LLMBasedIntentAnalyzer()
    print("✅ LLM意图分析器实例创建成功")
    
    # 检查是否有核心方法
    methods = ['analyze_intent_with_llm', 'check_intent_confidence', 'fuse_results']
    for method in methods:
        if hasattr(analyzer, method):
            print(f"  ✅ 方法 {method} 存在")
        else:
            print(f"  ❌ 方法 {method} 不存在")
            
except ImportError as e:
    print(f"❌ LLM意图分析器类不存在: {e}")
except Exception as e:
    print(f"❌ LLM意图分析器创建失败: {e}")

# 2. 检查LLMBasedIntentAnalyzer是否真实存在于代码中
print("\\n🔍 搜索LLMBasedIntentAnalyzer定义:")
import subprocess
result = subprocess.run(['grep', '-r', 'LLMBasedIntentAnalyzer', './src'], capture_output=True, text=True)
if result.returncode == 0:
    lines = result.stdout.strip().split('\\n')
    print(f"  找到 {len(lines)-1} 个相关定义:")
    for line in lines[1:]:  # 跳过首行
        if line:
            print(f"    {line}")
else:
    print("  未找到LLMBasedIntentAnalyzer定义")

# 3. 检查HybridIntentRecognizer是否真实实现
print("\\n🔍 搜索HybridIntentRecognizer定义:")
result2 = subprocess.run(['grep', '-r', 'HybridIntentRecognizer', './src'], capture_output=True, text=True)
if result2.returncode == 0:
    lines = result2.stdout.strip().split('\\n')
    print(f"  找到 {len(lines)-1} 个相关定义:")
    for line in lines[1:]:  # 跳过首行
        if line:
            print(f"    {line}")
else:
    print("  未找到HybridIntentRecognizer定义")

# 4. 检查实际存在的意图分析器
print("\\n🔍 检查实际存在的意图分析器:")
import os
for root, dirs, files in os.walk('./src'):
    for file in files:
        if file.endswith('.py') and ('intent' in file.lower() or 'recogniz' in file.lower()):
            full_path = os.path.join(root, file)
            print(f"  检查文件: {full_path}")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 检查是否包含LLM相关关键词
                if 'llm' in content.lower() or 'model_provider' in content.lower():
                    print(f"    ⚡ 包含LLM相关代码")
                    # 检查是否有大模型调用方法
                    if 'generate(' in content or 'model_provider' in content:
                        print(f"    🤖 真实包含大模型调用")
                        
                    # 检查是否包含意图分析方法
                    if 'analyze' in content.lower() and ('intent' in content.lower() or 'recognize' in content.lower()):
                        print(f"    🎯 包含意图分析方法")
                        
                # 查找相关类名
                classes = ['LLMBasedIntentAnalyzer', 'HybridIntentRecognizer', 'MultiAgentIntentAnalyzer']
                for cls in classes:
                    if cls in content:
                        print(f"    🏷️  包含类: {cls}")

print("\\n🔧 实际意图识别流程检查:")

# 5. 检查意图识别器中大模型调用的真实实现
try:
    from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
    recognizer = EnhancedIntentRecognizer()
    print("✅ EnhancedIntentRecognizer加载成功")
    
    # 检查是否包含LLM相关属性
    if hasattr(recognizer, 'model_provider') or hasattr(recognizer, 'llm_analyzer'):
        print("  ⚡ 包含LLM分析组件")
    else:
        print("  ❌ 不包含LLM分析组件")
        
    # 检查是否有大模型分析方法
    llm_methods = ['analyze_with_llm', 'call_large_model', 'use_llm_for_analysis']
    for method in llm_methods:
        if hasattr(recognizer, method):
            print(f"  ✅ 包含LLM方法: {method}")
except Exception as e:
    print(f"❌ EnhancedIntentRecognizer检查失败: {e}")

print("\\n📋 当前意图识别流程总结:")
print("1. 现有的意图识别流程:")
print("   - 基于正则表达式的规则匹配")
print("   - 模式优先级匹配")
print("   - 参数提取和澄清机制")
print("   - 但可能缺少真正的LLM意图分析")
print()
print("2. 混合意图识别的目标设计:")
print("   - 规则匹配用于高置信度意图")
print("   - 大模型用于复杂或模糊意图")
print("   - 结果融合以提高准确性")
print()
print("3. 需要实现:")
print("   - 真实的大模型意图分析器")
print("   - 结果融合机制")
print("   - 性能优化以避免过多LLM调用")