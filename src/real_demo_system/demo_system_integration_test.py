"""真实演示系统集成测试

测试完整的演示系统集成，包括AI伦理决策分析场景的端到端执行。
"""

import asyncio
import json
import logging
import os

# 导入演示系统组件
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from real_demo_system.real_demo_controller import RealDemoController

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_ai_ethics_scenario():
    """测试AI伦理决策分析场景"""
    print("\n" + "="*60)
    print("测试 AI伦理决策分析场景")
    print("="*60)
    
    # 创建演示控制器
    demo_controller = RealDemoController({
        "llm": {
            "provider": "ollama",
            "ollama": {
                "host": "http://localhost:11434",
                "generation_model": "llama3:instruct"
            }
        }
    })
    
    # 创建演示会话
    print("\n1. 创建演示会话...")
    session_id = await demo_controller.create_demo_session(
        session_name="AI伦理决策分析演示",
        scenario_type="ai_ethics",
        participants=["AI Ethics", "economist", "product_manager"],
        metadata={
            "demo_purpose": "展示DAIP-LIVE系统的AI伦理分析能力",
            "audience": "技术决策者"
        }
    )
    print(f"会话创建成功: {session_id}")
    
    # 等待会话初始化
    await asyncio.sleep(2)
    
    # 检查会话状态
    print("\n2. 检查会话状态...")
    session_status = await demo_controller.get_session_status(session_id)
    print(f"会话状态: {session_status['status']}")
    print(f"参与者: {session_status['participants']}")
    
    # 执行AI伦理场景
    print("\n3. 执行AI伦理决策分析场景...")
    ethical_dilemma = """
    一家医疗AI公司开发了一个诊断系统，该系统在临床试验中显示出比人类医生更高的准确率。
    然而，该系统在处理少数族裔患者数据时准确率明显下降，这可能导致医疗不公平。
    公司面临以下选择：
    1. 立即发布系统，因为整体准确率更高，可以拯救更多生命
    2. 延迟发布，直到解决偏见问题，但这可能导致本可以拯救的生命失去
    3. 发布系统但明确标注其局限性，让医生自行判断
    
    请分析这个伦理困境并提供决策建议。
    """
    
    context = {
        "industry": "医疗AI",
        "stakeholders": ["患者", "医生", "AI公司", "监管机构", "保险公司"],
        "ethical_frameworks": ["功利主义", "义务论", "美德伦理学", "关怀伦理学"]
    }
    
    try:
        result = await demo_controller.execute_ai_ethics_scenario(
            session_id=session_id,
            ethical_dilemma=ethical_dilemma,
            context=context
        )
        
        print("\n4. 场景执行结果:")
        print(f"成功: {result['success']}")
        
        if result['success']:
            print(f"场景类型: {result['scenario_type']}")
            print(f"会话时长: {result['session_duration_ms']}ms")
            
            # 显示批判性审查结果
            if result['critical_review']['success']:
                print("\n批判性审查:")
                print(f"  - 原始内容长度: {len(result['critical_review']['original_content'])}")
                print(f"  - 最终内容长度: {len(result['critical_review']['final_content'])}")
                print(f"  - 是否需要修订: {result['critical_review']['revision_needed']}")
                print(f"  - 提取事实数: {result['critical_review']['facts_extracted']}")
                print(f"  - 审查事实数: {result['critical_review']['facts_reviewed']}")
            
            # 显示多视角分析结果
            if result['multi_perspective']['success']:
                print("\n多视角分析:")
                print(f"  - 分析主题: {result['multi_perspective']['topic']}")
                print(f"  - 视角数量: {len(result['multi_perspective']['perspectives'])}")
                print(f"  - 置信度: {result['multi_perspective']['confidence']}")
                print(f"  - 质量分数: {result['multi_perspective']['quality_score']}")
            
            # 显示综合分析
            if result['synthesis']['call_record']['success']:
                print("\n综合分析:")
                print(f"  - 调用ID: {result['synthesis']['call_record']['call_id']}")
                print(f"  - 响应时间: {result['synthesis']['call_record']['duration_ms']}ms")
                print(f"  - 输入Token: {result['synthesis']['call_record']['input_tokens']}")
                print(f"  - 输出Token: {result['synthesis']['call_record']['output_tokens']}")
                print(f"  - 响应长度: {len(result['synthesis']['response'])}")
                print(f"  - 响应预览: {result['synthesis']['response'][:300]}...")
            
            # 显示验证结果
            print("\n验证结果:")
            for verification in result['verification_results']:
                print(f"  - 类型: {verification['type']}")
                if verification['type'] == 'llm_call':
                    print(f"    调用ID: {verification['call_id']}")
                    print(f"    验证状态: {verification['verification']['status']}")
                    print(f"    置信度: {verification['verification']['confidence_score']}")
                elif verification['type'] == 'workflow_execution':
                    print(f"    执行ID: {verification['execution_id']}")
                    print(f"    透明度分数: {verification['verification']['transparency_score']}")
            
            # 显示透明度证书
            print("\n透明度证书:")
            cert = result['transparency_certificate']
            print(f"  - 证书ID: {cert['certificate_id']}")
            print(f"  - 颁发时间: {cert['issued_at']}")
            print(f"  - 证书哈希: {cert['certificate_hash'][:16]}...")
            
        else:
            print(f"执行失败: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"场景执行异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 获取系统状态
    print("\n5. 系统状态:")
    system_status = demo_controller.get_system_status()
    print(json.dumps(system_status, indent=2, ensure_ascii=False))
    
    # 获取演示统计
    print("\n6. 演示统计:")
    demo_stats = demo_controller.get_demo_statistics()
    print(json.dumps(demo_stats, indent=2, ensure_ascii=False))
    
    return demo_controller


async def test_product_strategy_scenario(demo_controller):
    """测试产品策略评估场景"""
    print("\n" + "="*60)
    print("测试 产品策略评估场景")
    print("="*60)
    
    # 创建新的演示会话
    print("\n1. 创建产品策略评估会话...")
    session_id = await demo_controller.create_demo_session(
        session_name="产品策略评估演示",
        scenario_type="product_strategy",
        participants=["product_manager", "economist"],
        metadata={
            "demo_purpose": "展示产品策略分析能力",
            "audience": "产品经理和投资者"
        }
    )
    print(f"会话创建成功: {session_id}")
    
    # 等待会话初始化
    await asyncio.sleep(2)
    
    # 执行产品策略场景
    print("\n2. 执行产品策略评估场景...")
    product_description = """
    一款基于AI的个人健康管理应用，能够：
    1. 通过可穿戴设备收集用户健康数据
    2. 使用机器学习算法分析健康趋势
    3. 提供个性化的健康建议和预警
    4. 连接医疗专业人士进行远程咨询
    5. 集成营养、运动、睡眠等全方位健康管理功能
    
    目标用户：关注健康的中高收入人群，年龄25-55岁
    商业模式：订阅制 + 增值服务
    """
    
    market_context = {
        "market_size": "全球数字健康市场预计2025年达到6590亿美元",
        "competitors": ["Apple Health", "Google Fit", "Fitbit", "MyFitnessPal"],
        "trends": ["个性化医疗", "预防性健康管理", "AI驱动的健康分析"],
        "regulations": ["HIPAA合规", "GDPR数据保护", "FDA医疗设备认证"]
    }
    
    try:
        result = await demo_controller.execute_product_strategy_scenario(
            session_id=session_id,
            product_description=product_description,
            market_context=market_context
        )
        
        print("\n3. 场景执行结果:")
        print(f"成功: {result['success']}")
        
        if result['success']:
            print(f"场景类型: {result['scenario_type']}")
            print(f"会话时长: {result['session_duration_ms']}ms")
            
            # 显示策略分析结果
            if result['strategy_analysis']['success']:
                print("\n策略分析:")
                print(f"  - 分析主题: {result['strategy_analysis']['topic']}")
                print(f"  - 分析视角: {result['strategy_analysis']['perspectives']}")
                print(f"  - 置信度: {result['strategy_analysis']['confidence']}")
                print(f"  - 质量分数: {result['strategy_analysis']['quality_score']}")
            
            # 显示策略建议
            if result['strategy_recommendations']['call_record']['success']:
                print("\n策略建议:")
                print(f"  - 调用ID: {result['strategy_recommendations']['call_record']['call_id']}")
                print(f"  - 响应时间: {result['strategy_recommendations']['call_record']['duration_ms']}ms")
                print(f"  - 建议长度: {len(result['strategy_recommendations']['response'])}")
                print(f"  - 建议预览: {result['strategy_recommendations']['response'][:300]}...")
        
        else:
            print(f"执行失败: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"场景执行异常: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主测试函数"""
    print("开始真实演示系统集成测试...")
    print(f"测试时间: {datetime.now().isoformat()}")
    
    try:
        # 测试AI伦理决策分析场景
        demo_controller = await test_ai_ethics_scenario()
        
        # 测试产品策略评估场景
        await test_product_strategy_scenario(demo_controller)
        
        print("\n" + "="*60)
        print("所有集成测试完成!")
        print("="*60)
        
        # 生成最终测试报告
        final_stats = demo_controller.get_demo_statistics()
        print("\n最终系统统计:")
        print(json.dumps(final_stats, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"集成测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())