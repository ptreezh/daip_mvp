#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复MemAgent初始化问题的脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def fix_integrated_llm_manager():
    """修复IntegratedLLMManager中的MemAgent初始化问题"""
    
    file_path = "src/core_services/integrated_llm_manager.py"
    
    # 读取原文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换有问题的初始化代码
    old_code = """    def __init__(self):
        \"\"\"初始化LLM管理器\"\"\"
        self.context_optimizer = IntelligentContextOptimizer()
        self.role_manager = RoleManager()
        self.memory_agent = MemAgent()"""
    
    new_code = """    def __init__(self):
        \"\"\"初始化LLM管理器\"\"\"
        self.context_optimizer = IntelligentContextOptimizer()
        self.role_manager = RoleManager()
        
        # 安全初始化MemAgent，支持优雅降级
        self.memory_agent = self._initialize_memory_agent()"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✅ 已修复IntegratedLLMManager的__init__方法")
    else:
        print("⚠️ 未找到需要修复的代码模式")
    
    # 添加安全初始化方法
    init_method = '''
    def _initialize_memory_agent(self):
        """安全初始化MemAgent，支持优雅降级"""
        try:
            from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
            from src.core_services.memory_agent import MemAgent
            
            # 尝试初始化EnhancedSSKGManager
            sskg_manager = EnhancedSSKGManager()
            memory_agent = MemAgent(sskg_manager=sskg_manager, enable_rl=False)
            
            logger.info("MemAgent initialized successfully")
            return memory_agent
            
        except ImportError as e:
            logger.warning(f"MemAgent dependencies not available: {e}")
            return None
        except Exception as e:
            logger.warning(f"MemAgent initialization failed: {e}")
            return None
'''
    
    # 在类的末尾添加新方法（在最后一个方法之后）
    if "_initialize_memory_agent" not in content:
        # 找到类的最后一个方法
        lines = content.split('\n')
        insert_index = -1
        
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line and not line.startswith('#') and not line.startswith('"""'):
                # 找到类的结束位置
                if line and not line.startswith(' '):
                    insert_index = i
                    break
        
        if insert_index > 0:
            lines.insert(insert_index, init_method)
            content = '\n'.join(lines)
            print("✅ 已添加_initialize_memory_agent方法")
        else:
            # 如果找不到合适的位置，就添加到文件末尾
            content += init_method
            print("✅ 已在文件末尾添加_initialize_memory_agent方法")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修复文件: {file_path}")


def fix_academic_research_scenario():
    """修复AcademicResearchScenario中的MemAgent初始化问题"""
    
    file_path = "src/scenarios/academic_research_scenario.py"
    
    # 读取原文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换有问题的初始化代码
    old_pattern = """        # 记忆代理 - 使用简化初始化
        try:
            from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
            sskg_manager = EnhancedSSKGManager()
            self.memory_agent = MemAgent(sskg_manager=sskg_manager, enable_rl=False)
        except Exception as e:
            logger.warning(f"Memory agent initialization failed: {e}")
            self.memory_agent = None"""
    
    new_pattern = """        # 记忆代理 - 使用安全初始化
        self.memory_agent = self._safe_initialize_memory_agent()"""
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("✅ 已修复AcademicResearchScenario的MemAgent初始化")
    else:
        print("⚠️ AcademicResearchScenario中未找到需要修复的代码模式")
    
    # 添加安全初始化方法
    safe_init_method = '''
    def _safe_initialize_memory_agent(self):
        """安全初始化MemAgent"""
        try:
            from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
            from src.core_services.memory_agent import MemAgent
            
            sskg_manager = EnhancedSSKGManager()
            memory_agent = MemAgent(sskg_manager=sskg_manager, enable_rl=False)
            logger.info("Memory agent initialized successfully")
            return memory_agent
            
        except ImportError as e:
            logger.warning(f"Memory agent dependencies not available: {e}")
            return None
        except Exception as e:
            logger.warning(f"Memory agent initialization failed: {e}")
            return None
'''
    
    if "_safe_initialize_memory_agent" not in content:
        # 在类的适当位置添加方法
        content += safe_init_method
        print("✅ 已添加_safe_initialize_memory_agent方法")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修复文件: {file_path}")


def create_dependency_validator():
    """创建依赖关系验证器"""
    
    validator_code = '''#!/usr/bin/env python3
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
            print(f"\\n验证 {name}...")
            validation_func()
        
        # 显示结果
        print("\\n" + "=" * 50)
        print("📊 验证结果:")
        
        passed = 0
        total = len(self.validation_results)
        
        for service, result in self.validation_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {service}: {status}")
            if result:
                passed += 1
        
        print(f"\\n总体结果: {passed}/{total} 项通过")
        
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
'''
    
    with open("dependency_validator.py", 'w', encoding='utf-8') as f:
        f.write(validator_code)
    
    print("✅ 已创建依赖关系验证器: dependency_validator.py")


def main():
    """主函数"""
    print("🔧 开始修复MemAgent初始化问题")
    print("=" * 50)
    
    try:
        # 1. 修复IntegratedLLMManager
        print("\\n1️⃣ 修复IntegratedLLMManager...")
        fix_integrated_llm_manager()
        
        # 2. 修复AcademicResearchScenario
        print("\\n2️⃣ 修复AcademicResearchScenario...")
        fix_academic_research_scenario()
        
        # 3. 创建依赖验证器
        print("\\n3️⃣ 创建依赖关系验证器...")
        create_dependency_validator()
        
        print("\\n" + "=" * 50)
        print("🎉 MemAgent初始化问题修复完成！")
        print("\\n📋 后续步骤:")
        print("1. 运行 python dependency_validator.py 验证修复效果")
        print("2. 运行原有的验证脚本确认问题已解决")
        print("3. 考虑重构为依赖注入架构（长期计划）")
        
        return True
        
    except Exception as e:
        print(f"\\n❌ 修复过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)