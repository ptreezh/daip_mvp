#!/usr/bin/env python3
"""验证LLM调用验证机制
"""

import asyncio
import sys

sys.path.append('src')

def test_call_verification():
    """测试调用验证"""
    try:
        from src.real_demo_system.call_verification import CallVerificationSystem

        # 创建验证器
        verifier = CallVerificationSystem()

        # 验证基本属性
        assert hasattr(verifier, 'audit_log'), "缺少audit_log属性"
        assert hasattr(verifier, 'verification_cache'), "缺少verification_cache属性"
        assert hasattr(verifier, 'hash_chain'), "缺少hash_chain属性"

        # 验证基本方法
        assert hasattr(verifier, 'generate_call_signature'), "缺少generate_call_signature方法"
        assert hasattr(verifier, 'verify_call_signature'), "缺少verify_call_signature方法"
        assert hasattr(verifier, 'verify_call_integrity'), "缺少verify_call_integrity方法"

        print("✅ CallVerificationSystem验证通过")
        return True

    except Exception as e:
        print(f"❌ CallVerificationSystem验证失败: {e}")
        return False

def test_signature_generation():
    """测试签名生成"""
    try:
        from datetime import datetime

        from src.real_demo_system.call_verification import CallVerificationSystem
        from src.real_demo_system.real_llm_integrator import LLMCallRecord

        verifier = CallVerificationSystem()

        # 创建测试调用记录
        call_record = LLMCallRecord(
            call_id="test_001",
            provider="ollama",
            model="gemma3:latest",
            prompt="测试提示",
            response="测试响应",
            timestamp=datetime.now(),
            duration_ms=1500,
            input_tokens=10,
            output_tokens=5,
            cost_usd=0.001,
            success=True,
            metadata={}
        )

        signature = verifier.generate_call_signature(call_record)
        assert isinstance(signature, str), "签名应为字符串"
        assert len(signature) > 0, "签名不能为空"

        print("✅ 签名生成验证通过")
        return True

    except Exception as e:
        print(f"❌ 签名生成验证失败: {e}")
        return False

def test_call_verification_process():
    """测试调用验证流程"""
    try:
        from datetime import datetime

        from src.real_demo_system.call_verification import CallVerificationSystem
        from src.real_demo_system.real_llm_integrator import LLMCallRecord

        verifier = CallVerificationSystem()

        # 创建测试调用记录
        call_record = LLMCallRecord(
            call_id="test_001",
            provider="ollama",
            model="gemma3:latest",
            prompt="测试提示",
            response="测试响应",
            timestamp=datetime.now(),
            duration_ms=1500,
            input_tokens=10,
            output_tokens=5,
            cost_usd=0.001,
            success=True,
            metadata={}
        )

        # 生成签名
        signature = verifier.generate_call_signature(call_record)

        # 验证签名
        is_valid = verifier.verify_call_signature(call_record, signature)
        assert is_valid == True, "签名验证应该通过"

        # 验证调用完整性
        result = verifier.verify_call_integrity(call_record)
        assert hasattr(result, 'status'), "验证结果缺少status"
        assert hasattr(result, 'confidence_score'), "验证结果缺少confidence_score"

        print("✅ 调用验证流程验证通过")
        return True

    except Exception as e:
        print(f"❌ 调用验证流程验证失败: {e}")
        return False

def test_integrity_check():
    """测试完整性检查"""
    try:
        from src.real_demo_system.call_verification import CallVerificationSystem

        verifier = CallVerificationSystem()

        # 验证审计功能
        assert hasattr(verifier, 'get_verification_summary'), "缺少get_verification_summary方法"
        assert hasattr(verifier, 'generate_audit_trail'), "缺少generate_audit_trail方法"

        # 获取验证摘要
        summary = verifier.get_verification_summary()
        assert isinstance(summary, dict), "验证摘要应为字典"
        assert "total_verifications" in summary, "验证摘要缺少total_verifications"
        assert "verification_stats" in summary, "验证摘要缺少verification_stats"
        assert "audit_stats" in summary, "验证摘要缺少audit_stats"

        print("✅ 完整性检查验证通过")
        return True

    except Exception as e:
        print(f"❌ 完整性检查验证失败: {e}")
        return False

async def test_llm_integration_verification():
    """测试LLM集成服务的验证功能"""
    try:
        from src.real_demo_system.llm_integration_service import LLMBackend, LLMIntegrationService

        service = LLMIntegrationService()

        # 执行调用
        response = await service.generate(
            prompt="验证测试",
            backend=LLMBackend.OLLAMA,
            temperature=0.1,
            max_tokens=20
        )

        # 验证响应包含验证信息
        assert hasattr(response, 'call_record'), "响应缺少call_record"
        call_record = response.call_record

        if call_record:
            assert hasattr(call_record, 'signature'), "调用记录缺少signature"
            assert hasattr(call_record, 'hash'), "调用记录缺少hash"
            assert len(call_record.signature) > 0, "signature不能为空"
            assert len(call_record.hash) > 0, "hash不能为空"

        # 验证完整性检查
        integrity = service.verify_call_integrity()
        assert "valid" in integrity, "完整性检查缺少valid"
        assert "message" in integrity, "完整性检查缺少message"

        print("✅ LLM集成服务验证功能验证通过")
        return True

    except Exception as e:
        print(f"❌ LLM集成服务验证功能验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证LLM调用验证机制")

    tests = [
        ("CallVerification", test_call_verification),
        ("签名生成", test_signature_generation),
        ("调用验证流程", test_call_verification_process),
        ("完整性检查", test_integrity_check),
        ("LLM集成服务验证", test_llm_integration_verification)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 验证 {test_name}...")
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()

        if result:
            passed += 1
        else:
            print(f"❌ {test_name} 验证失败，停止后续测试")
            break

    if passed == total:
        print(f"\n✅ 所有验证通过 ({passed}/{total})")
        return True
    else:
        print(f"\n❌ 验证失败 ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
