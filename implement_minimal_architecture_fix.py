#!/usr/bin/env python3
"""
最小化架构修复方案
工作量：3-5天，解决核心依赖问题
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Type

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class ServiceFactory:
    """服务工厂 - 解决依赖注入问题的最小化方案"""
    
    _instances: Dict[str, Any] = {}
    _factories: Dict[str, callable] = {}
    
    @classmethod
    def register_factory(cls, service_name: str, factory_func: callable):
        """注册服务工厂函数"""
        cls._factories[service_name] = factory_func
        logger.info(f"Registered factory for {service_name}")
    
    @classmethod
    def get_service(cls, service_name: str, **kwargs) -> Optional[Any]:
        """获取服务实例（单例模式）"""
        if service_name not in cls._instances:
            if service_name in cls._factories:
                try:
                    cls._instances[service_name] = cls._factories[service_name](**kwargs)
                    logger.info(f"Created service instance: {service_name}")
                except Exception as e:
                    logger.error(f"Failed to create {service_name}: {e}")
                    return None
            else:
                logger.warning(f"No factory registered for {service_name}")
                return None
        
        return cls._instances[service_name]
    
    @classmethod
    def clear_cache(cls):
        """清除缓存（用于测试）"""
        cls._instances.clear()


def create_service_factories():
    """创建所有服务的工厂函数"""
    
    def create_enhanced_sskg_manager():
        """创建EnhancedSSKGManager"""
        try:
            from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
            return EnhancedSSKGManager()
        except Exception as e:
            logger.warning(f"EnhancedSSKGManager creation failed: {e}")
            return None
    
    def create_memory_agent():
        """创建MemAgent"""
        try:
            from src.core_services.memory_agent import MemAgent
            sskg_manager = ServiceFactory.get_service("enhanced_sskg_manager")
            if sskg_manager:
                return MemAgent(sskg_manager=sskg_manager, enable_rl=False)
            else:
                logger.warning("Cannot create MemAgent: EnhancedSSKGManager not available")
                return None
        except Exception as e:
            logger.warning(f"MemAgent creation failed: {e}")
            return None    
  
  def create_integrated_llm_manager():
        """创建IntegratedLLMManager"""
        try:
            # 先确保依赖服务可用
            memory_agent = ServiceFactory.get_service("memory_agent")
            
            # 动态修改IntegratedLLMManager的初始化
            from src.core_services.integrated_llm_manager import IntegratedLLMManager
            
            # 创建实例
            manager = object.__new__(IntegratedLLMManager)
            
            # 手动初始化（绕过原有的__init__）
            from src.core_services.intelligent_context_optimizer import IntelligentContextOptimizer
            from src.core_services.role_manager import RoleManager
            
            manager.context_optimizer = IntelligentContextOptimizer()
            manager.role_manager = RoleManager()
            manager.memory_agent = memory_agent  # 可能为None，但不会报错
            
            # 初始化其他属性
            manager.role_contexts = {}
            manager.call_history = []
            manager.performance_stats = {
                "total_calls": 0,
                "total_tokens_saved": 0,
                "total_time_saved": 0.0,
                "average_improvement": 0.0
            }
            
            logger.info("IntegratedLLMManager created with safe initialization")
            return manager
            
        except Exception as e:
            logger.error(f"IntegratedLLMManager creation failed: {e}")
            return None
    
    # 注册所有工厂函数
    ServiceFactory.register_factory("enhanced_sskg_manager", create_enhanced_sskg_manager)
    ServiceFactory.register_factory("memory_agent", create_memory_agent)
    ServiceFactory.register_factory("integrated_llm_manager", create_integrated_llm_manager)


class HealthChecker:
    """服务健康检查器"""
    
    @staticmethod
    def check_service_health() -> Dict[str, str]:
        """检查所有服务的健康状态"""
        health_status = {}
        
        services_to_check = [
            "enhanced_sskg_manager",
            "memory_agent", 
            "integrated_llm_manager"
        ]
        
        for service_name in services_to_check:
            try:
                service = ServiceFactory.get_service(service_name)
                if service is not None:
                    health_status[service_name] = "healthy"
                else:
                    health_status[service_name] = "unavailable"
            except Exception as e:
                health_status[service_name] = f"error: {str(e)[:50]}"
        
        return health_status
    
    @staticmethod
    def print_health_report():
        """打印健康检查报告"""
        print("🏥 服务健康检查报告")
        print("=" * 40)
        
        health_status = HealthChecker.check_service_health()
        
        for service_name, status in health_status.items():
            if status == "healthy":
                print(f"✅ {service_name}: {status}")
            elif status == "unavailable":
                print(f"⚠️ {service_name}: {status}")
            else:
                print(f"❌ {service_name}: {status}")
        
        healthy_count = sum(1 for status in health_status.values() if status == "healthy")
        total_count = len(health_status)
        
        print(f"\n📊 总体状态: {healthy_count}/{total_count} 服务健康")
        
        return healthy_count == total_count


def patch_academic_research_scenario():
    """修补AcademicResearchScenario使用服务工厂"""
    
    patch_code = '''
    # 在AcademicResearchScenario.__init__中替换原有的初始化代码
    
    def __init__(self):
        """初始化学术研究场景，使用服务工厂"""
        # 确保服务工厂已初始化
        from implement_minimal_architecture_fix import ServiceFactory, create_service_factories
        create_service_factories()
        
        # 使用服务工厂获取依赖
        self.llm_manager = ServiceFactory.get_service("integrated_llm_manager")
        
        # 其他初始化保持不变...
    '''
    
    print("📝 AcademicResearchScenario修补代码已生成")
    print("请手动将以上代码应用到AcademicResearchScenario.__init__方法中")


def main():
    """主函数 - 演示最小化架构修复"""
    print("🔧 最小化架构修复方案")
    print("=" * 50)
    
    # 1. 初始化服务工厂
    print("\n1️⃣ 初始化服务工厂...")
    create_service_factories()
    
    # 2. 健康检查
    print("\n2️⃣ 执行健康检查...")
    is_healthy = HealthChecker.print_health_report()
    
    # 3. 测试服务获取
    print("\n3️⃣ 测试服务获取...")
    
    services_to_test = ["enhanced_sskg_manager", "memory_agent", "integrated_llm_manager"]
    
    for service_name in services_to_test:
        service = ServiceFactory.get_service(service_name)
        if service:
            print(f"✅ {service_name}: {type(service).__name__}")
        else:
            print(f"❌ {service_name}: 获取失败")
    
    # 4. 生成修补代码
    print("\n4️⃣ 生成修补代码...")
    patch_academic_research_scenario()
    
    print("\n" + "=" * 50)
    if is_healthy:
        print("🎉 最小化架构修复成功！")
        print("\n📋 下一步:")
        print("1. 将修补代码应用到相关类中")
        print("2. 运行测试验证修复效果")
        print("3. 考虑后续的完整重构计划")
    else:
        print("⚠️ 部分服务仍有问题，需要进一步调试")
    
    return is_healthy


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)