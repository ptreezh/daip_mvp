#!/usr/bin/env python3
"""Simple test script for the Judao-Mo AI system
"""

import asyncio
import os
import sys

# Add project path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from judao_mo_ai_tested_demo import JudaoMoAIEngine


async def test_system():
    """Test the core system functionality"""
    print("=" * 50)
    print("Testing Judao-Mo AI System")
    print("=" * 50)
    
    engine = JudaoMoAIEngine()
    
    # Wait for LLM check
    await asyncio.sleep(2)
    
    try:
        # Test 1: Expert Consultation
        print("\n1. Testing Expert Consultation...")
        consultation = await engine.expert_consultation("我们应该投资区块链技术吗？", "investment")
        assert len(consultation.expert_opinions) >= 3, "Expert count insufficient"
        assert consultation.confidence_score > 0.7, "Confidence too low"
        assert len(consultation.final_judgment) > 200, "Judgment too short"
        print("✅ Expert consultation test passed")
        
        # Test 2: Academic Research
        print("\n2. Testing Academic Research...")
        academic = await engine.academic_research("机器学习在医疗诊断中的应用")
        assert len(academic.expert_opinions) >= 3, "Scholar count insufficient"
        assert academic.confidence_score > 0.8, "Academic quality too low"
        assert "学术" in academic.final_judgment, "Missing academic content"
        print("✅ Academic research test passed")
        
        # Test 3: Industry Research
        print("\n3. Testing Industry Research...")
        industry = await engine.industry_research("新能源汽车")
        assert len(industry.expert_opinions) >= 3, "Analyst count insufficient"
        assert industry.confidence_score > 0.8, "Analysis quality too low"
        assert "行业" in industry.final_judgment, "Missing industry content"
        print("✅ Industry research test passed")
        
        print("\n" + "=" * 50)
        print("🎉 All functionality tests passed!")
        print(f"LLM Available: {'Yes' if engine.llm_available else 'No (Simulation mode)'}")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    result = asyncio.run(test_system())
    sys.exit(0 if result else 1)