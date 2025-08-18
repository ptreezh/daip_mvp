#!/usr/bin/env python3
"""Simple test script for the Judao-Mo AI system (Windows compatible)
"""

import asyncio
import os
import sys

# Fix Unicode output for Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Add project path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import with error handling
try:
    from judao_mo_ai_tested_demo import JudaoMoAIEngine
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)

async def test_system():
    """Test the core system functionality"""
    print("=" * 50)
    print("Testing Judao-Mo AI System")
    print("=" * 50)
    
    try:
        engine = JudaoMoAIEngine()
        
        # Wait for LLM check
        await asyncio.sleep(3)
        
        # Test 1: Expert Consultation
        print("\n1. Testing Expert Consultation...")
        consultation = await engine.expert_consultation("Should we invest in blockchain technology?", "investment")
        
        print(f"   - Expert count: {len(consultation.expert_opinions)}")
        print(f"   - Confidence: {consultation.confidence_score:.2f}")
        print(f"   - Judgment length: {len(consultation.final_judgment)}")
        
        assert len(consultation.expert_opinions) >= 3, f"Expert count insufficient: {len(consultation.expert_opinions)}"
        assert consultation.confidence_score > 0.7, f"Confidence too low: {consultation.confidence_score}"
        assert len(consultation.final_judgment) > 200, f"Judgment too short: {len(consultation.final_judgment)}"
        print("   Status: PASSED")
        
        # Test 2: Academic Research
        print("\n2. Testing Academic Research...")
        academic = await engine.academic_research("AI applications in healthcare")
        
        print(f"   - Scholar count: {len(academic.expert_opinions)}")
        print(f"   - Academic quality: {academic.confidence_score:.2f}")
        print(f"   - Report length: {len(academic.final_judgment)}")
        
        assert len(academic.expert_opinions) >= 3, f"Scholar count insufficient: {len(academic.expert_opinions)}"
        assert academic.confidence_score > 0.8, f"Academic quality too low: {academic.confidence_score}"
        print("   Status: PASSED")
        
        # Test 3: Industry Research
        print("\n3. Testing Industry Research...")
        industry = await engine.industry_research("Electric Vehicle Industry")
        
        print(f"   - Analyst count: {len(industry.expert_opinions)}")
        print(f"   - Analysis quality: {industry.confidence_score:.2f}")
        print(f"   - Report length: {len(industry.final_judgment)}")
        
        assert len(industry.expert_opinions) >= 3, f"Analyst count insufficient: {len(industry.expert_opinions)}"
        assert industry.confidence_score > 0.8, f"Analysis quality too low: {industry.confidence_score}"
        print("   Status: PASSED")
        
        print("\n" + "=" * 50)
        print("SUCCESS: All functionality tests passed!")
        print(f"LLM Available: {'Yes' if engine.llm_available else 'No (Simulation mode)'}")
        print("=" * 50)
        return True
        
    except AssertionError as e:
        print(f"\nASSERTION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\nERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    result = asyncio.run(test_system())
    print(f"\nFinal result: {'PASS' if result else 'FAIL'}")
    sys.exit(0 if result else 1)