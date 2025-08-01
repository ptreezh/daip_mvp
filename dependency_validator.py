#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖关系验证器
用于检查系统中所有服务的依赖关系是否正确
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class DependencyValidator:
    """依赖关系验证器"""
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_enhanced_sskg_manager(self):
        """验证EnhancedSSKGManager"""
        try:
            from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
            manager = EnhancedSSKGManager()
            self.validation_results['EnhancedSSKGManager'] = True
            logger.info("✅ EnhancedSSKGManager validation passed")
            return True
        except Exception as e:
            self.validation_results['EnhancedSSKGManager'] = False
            logger.error(f"❌ EnhancedSSKGManager validation failed: {e}")
            return False
    
    def validate_memory_agent(self):
        """验证MemAgent"""
        try:
            from src.core_services.memory_agent import MemAgent
            from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
            
            sskg_manager = EnhancedSSKGManager()
            agent = MemAgent(sskg_manager=sskg_manager, enable_rl=False)
            self.validation_results['MemAgent'] = True
            logger.info("✅ MemAgent validation passed")
            return True
        except Exception as e:
            self.validation_results['MemAgent'] = False
            logger.error(f"❌ MemAgent validation failed: {e}")
            return False
    
    def validate_integrated_llm_manager(self):
        """验证IntegratedLLMManager"""
        try:
            from src.core_services.integrated_llm_manager import IntegratedLLMManager
            manager = IntegratedLLMManager()
            self.validation_results['IntegratedLLMManager'] = True
            logger.info("✅ IntegratedLLMManager validation passed")
            return True
        except Exception as e:
            self.validation_results['IntegratedLLMManager'] = False
            logger.error(f"❌ IntegratedLLMManager validation failed: {e}")
            return False
    
    def validate_academic_research_scenario(self):
        """验证AcademicResearchScenario"""
        try:
            from src.scenarios.academic_research_scenario import AcademicResearchScenario
            scenario = AcademicResearchScenario()
            self.validation_results['AcademicResearchScenario'] = True
            logger.info("✅ AcademicResearchScenario validation passed")
            return True
        except Exception as e:
            self.validation_results['AcademicResearchScenario'] = False
            logger.error(f"❌ AcademicResearchScenario validation failed: {e}")
            return False
    
    def run_all_validations(self):
        """运行所有验证"""
        print("🔍 开始依赖关系验证...")
        print("=" * 50)
        
        validations = [
            ("EnhancedSSKGManager", self.validate_enhanced_sskg_manager),
            ("MemAgent", self.validate_memory_agent),
            ("IntegratedLLMManager", self.validate_integrated_llm_manager),
            ("AcademicResearchScenario", self.validate_academic_research_scenario)
        ]
        
        for name, validation_func in validations:
            print(f"\n验证 {name}...")
            validation_func()
        
        # 显示结果
        print("\n" + "=" * 50)
        print("📊 验证结果:")
        
        passed = 0
        total = len(self.validation_results)
        
        for service, result in self.validation_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {service}: {status}")
            if result:
                passed += 1
        
        print(f"\n总体结果: {passed}/{total} 项通过")
        
        if passed == total:
            print("🎉 所有依赖关系验证通过！")
            return True
        else:
            print("⚠️ 部分依赖关系验证失败")
            return False


if __name__ == "__main__":
    validator = DependencyValidator()
    success = validator.run_all_validations()
    sys.exit(0 if success else 1)
