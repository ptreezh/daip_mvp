#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工程可用性验证
验证DAIP系统的工程可用性和用户体验
"""

import asyncio
import logging
import time
import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EngineeringUsabilityValidator:
    """工程可用性验证器"""
    
    def __init__(self):
        self.validation_results = {}
        self.start_time = datetime.now()
        
    async def run_validation(self) -> Dict[str, Any]:
        """运行完整的工程可用性验证"""
        print("=" * 80)
        print("🔧 DAIP-LIVE 工程可用性验证")
        print("=" * 80)
        
        try:
            # 1. 核心组件导入验证
            core_import_result = await self.validate_core_imports()
            
            # 2. 配置文件验证
            config_result = await self.validate_configurations()
            
            # 3. 角色系统验证
            role_system_result = await self.validate_role_system()
            
            # 4. 学术研究场景验证
            academic_scenario_result = await self.validate_academic_scenario()
            
            # 5. 专家咨询场景验证
            expert_consultation_result = await self.validate_expert_consultation()
            
            # 6. 文件系统验证
            file_system_result = await self.validate_file_system()
            
            # 7. 依赖验证
            dependency_result = await self.validate_dependencies()
            
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            
            # 生成综合报告
            final_report = {
                "success": True,
                "validation_summary": {
                    "start_time": self.start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration,
                    "total_checks": 7,
                    "passed_checks": 0
                },
                "detailed_results": {
                    "core_imports": core_import_result,
                    "configurations": config_result,
                    "role_system": role_system_result,
                    "academic_scenario": academic_scenario_result,
                    "expert_consultation": expert_consultation_result,
                    "file_system": file_system_result,
                    "dependencies": dependency_result
                },
                "engineering_assessment": {
                    "deployment_ready": False,
                    "user_ready": False,
                    "development_ready": False,
                    "overall_score": 0.0
                },
                "recommendations": []
            }
            
            # 计算成功率
            passed_checks = sum(1 for result in final_report["detailed_results"].values() if result.get("success", False))
            final_report["validation_summary"]["passed_checks"] = passed_checks
            success_rate = passed_checks / 7
            
            # 工程质量评估
            final_report["engineering_assessment"]["deployment_ready"] = success_rate >= 0.8
            final_report["engineering_assessment"]["user_ready"] = success_rate >= 0.7
            final_report["engineering_assessment"]["development_ready"] = success_rate >= 0.6
            final_report["engineering_assessment"]["overall_score"] = success_rate
            
            # 生成建议
            final_report["recommendations"] = self.generate_recommendations(final_report["detailed_results"])
            
            # 保存报告
            self.save_validation_report(final_report)
            
            # 打印摘要
            self.print_validation_summary(final_report)
            
            return final_report
            
        except Exception as e:
            logger.error(f"验证执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def validate_core_imports(self) -> Dict[str, Any]:
        """验证核心组件导入"""
        print("\n🔍 验证核心组件导入...")
        
        import_tests = []
        
        # 测试核心服务导入
        core_imports = [
            ("src.core_services.role_manager", "RoleManager"),
            ("src.core_services.integrated_llm_manager", "IntegratedLLMManager"),
            ("src.core_services.wiki_service", "WikiService"),
            ("src.core_services.advanced_consensus_algorithms", "WeightedVotingConsensus"),
            ("src.virtual_role_chat.cognitive_agent.agent", "CognitiveAgent"),
            ("src.scenarios.academic_research_scenario", "AcademicResearchScenario"),
            ("src.scenarios.expert_consultation_scenario", "ExpertConsultationScenario")
        ]
        
        for module_name, class_name in core_imports:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                import_tests.append({
                    "module": module_name,
                    "class": class_name,
                    "success": True,
                    "available": True
                })
                print(f"  ✓ {module_name}.{class_name}")
            except Exception as e:
                import_tests.append({
                    "module": module_name,
                    "class": class_name,
                    "success": False,
                    "error": str(e)
                })
                print(f"  ✗ {module_name}.{class_name} - {e}")
        
        success_count = sum(1 for test in import_tests if test["success"])
        success_rate = success_count / len(import_tests)
        
        return {
            "success": success_rate >= 0.8,
            "success_rate": success_rate,
            "total_imports": len(import_tests),
            "successful_imports": success_count,
            "import_details": import_tests
        }
    
    async def validate_configurations(self) -> Dict[str, Any]:
        """验证配置文件"""
        print("\n🔍 验证配置文件...")
        
        config_checks = []
        
        # 检查关键配置文件
        config_files = [
            "config.yaml",
            "pyproject.toml", 
            "CLAUDE.md",
            "roles/"
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                config_checks.append({
                    "file": config_file,
                    "exists": True,
                    "readable": config_path.is_file() or config_path.is_dir()
                })
                print(f"  ✓ {config_file}")
            else:
                config_checks.append({
                    "file": config_file,
                    "exists": False,
                    "readable": False
                })
                print(f"  ✗ {config_file} - 文件不存在")
        
        # 检查角色文件
        roles_dir = Path("roles")
        role_count = 0
        if roles_dir.exists():
            role_files = list(roles_dir.glob("*.json"))
            role_count = len(role_files)
            print(f"  ✓ 找到 {role_count} 个角色文件")
        
        success = all(check["exists"] for check in config_checks)
        
        return {
            "success": success,
            "config_files_found": sum(1 for check in config_checks if check["exists"]),
            "total_config_files": len(config_checks),
            "role_files_count": role_count,
            "config_details": config_checks
        }
    
    async def validate_role_system(self) -> Dict[str, Any]:
        """验证角色系统"""
        print("\n🔍 验证角色系统...")
        
        try:
            from src.core_services.role_manager import RoleManager
            
            role_manager = RoleManager()
            available_roles = role_manager.list_roles()
            
            role_validation = {
                "manager_initialized": True,
                "total_roles": len(available_roles),
                "role_names": [role.name for role in available_roles[:10]],  # 前10个角色
                "role_loading_success": len(available_roles) > 0
            }
            
            print(f"  ✓ 角色管理器初始化成功")
            print(f"  ✓ 加载了 {len(available_roles)} 个角色")
            
            return {
                "success": len(available_roles) > 0,
                "role_validation": role_validation
            }
            
        except Exception as e:
            print(f"  ✗ 角色系统验证失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_academic_scenario(self) -> Dict[str, Any]:
        """验证学术研究场景"""
        print("\n🔍 验证学术研究场景...")
        
        try:
            from src.scenarios.academic_research_scenario import AcademicResearchScenario
            
            # 创建场景实例
            scenario = AcademicResearchScenario()
            
            # 验证场景组件
            validation_checks = {
                "scenario_initialized": True,
                "cognitive_agent_available": hasattr(scenario, 'cognitive_agent'),
                "llm_manager_available": hasattr(scenario, 'llm_manager'),
                "role_manager_available": hasattr(scenario, 'role_manager'),
                "wiki_service_available": hasattr(scenario, 'wiki_service'),
                "consensus_algorithm_available": hasattr(scenario, 'consensus_algorithm')
            }
            
            success_count = sum(1 for check in validation_checks.values() if check)
            success_rate = success_count / len(validation_checks)
            
            print(f"  ✓ 学术研究场景初始化成功")
            print(f"  ✓ {success_count}/{len(validation_checks)} 组件可用")
            
            return {
                "success": success_rate >= 0.8,
                "success_rate": success_rate,
                "validation_checks": validation_checks
            }
            
        except Exception as e:
            print(f"  ✗ 学术研究场景验证失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_expert_consultation(self) -> Dict[str, Any]:
        """验证专家咨询场景"""
        print("\n🔍 验证专家咨询场景...")
        
        try:
            from src.scenarios.expert_consultation_scenario import ExpertConsultationScenario
            
            # 创建场景实例
            scenario = ExpertConsultationScenario()
            
            # 验证专家数据库
            expert_count = len(scenario.expert_profiles)
            expert_domains = set(expert.domain for expert in scenario.expert_profiles.values())
            
            validation_checks = {
                "scenario_initialized": True,
                "expert_database_loaded": expert_count > 0,
                "multiple_domains": len(expert_domains) >= 3,
                "llm_manager_available": hasattr(scenario, 'llm_manager'),
                "role_manager_available": hasattr(scenario, 'role_manager'),
                "consensus_algorithm_available": hasattr(scenario, 'consensus_algorithm')
            }
            
            success_count = sum(1 for check in validation_checks.values() if check)
            success_rate = success_count / len(validation_checks)
            
            print(f"  ✓ 专家咨询场景初始化成功")
            print(f"  ✓ 加载了 {expert_count} 位专家，覆盖 {len(expert_domains)} 个领域")
            
            return {
                "success": success_rate >= 0.8,
                "success_rate": success_rate,
                "expert_count": expert_count,
                "domain_count": len(expert_domains),
                "domains": list(expert_domains),
                "validation_checks": validation_checks
            }
            
        except Exception as e:
            print(f"  ✗ 专家咨询场景验证失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_file_system(self) -> Dict[str, Any]:
        """验证文件系统结构"""
        print("\n🔍 验证文件系统结构...")
        
        required_directories = [
            "src/",
            "src/core_services/",
            "src/scenarios/",
            "src/virtual_role_chat/",
            "src/workflows/",
            "roles/",
            "data/"
        ]
        
        directory_checks = []
        for directory in required_directories:
            dir_path = Path(directory)
            exists = dir_path.exists() and dir_path.is_dir()
            directory_checks.append({
                "directory": directory,
                "exists": exists
            })
            if exists:
                print(f"  ✓ {directory}")
            else:
                print(f"  ✗ {directory} - 目录不存在")
        
        success_count = sum(1 for check in directory_checks if check["exists"])
        success_rate = success_count / len(directory_checks)
        
        return {
            "success": success_rate >= 0.9,
            "success_rate": success_rate,
            "directories_found": success_count,
            "total_directories": len(directory_checks),
            "directory_details": directory_checks
        }
    
    async def validate_dependencies(self) -> Dict[str, Any]:
        """验证关键依赖"""
        print("\n🔍 验证关键依赖...")
        
        dependencies = [
            "asyncio",
            "logging", 
            "json",
            "pathlib",
            "datetime",
            "typing",
            "dataclasses",
            "uuid"
        ]
        
        dependency_checks = []
        for dep in dependencies:
            try:
                __import__(dep)
                dependency_checks.append({
                    "dependency": dep,
                    "available": True
                })
                print(f"  ✓ {dep}")
            except ImportError as e:
                dependency_checks.append({
                    "dependency": dep,
                    "available": False,
                    "error": str(e)
                })
                print(f"  ✗ {dep} - {e}")
        
        success_count = sum(1 for check in dependency_checks if check["available"])
        success_rate = success_count / len(dependency_checks)
        
        return {
            "success": success_rate >= 0.95,
            "success_rate": success_rate,
            "dependencies_available": success_count,
            "total_dependencies": len(dependency_checks),
            "dependency_details": dependency_checks
        }
    
    def generate_recommendations(self, detailed_results: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于各个验证结果生成建议
        if not detailed_results.get("core_imports", {}).get("success"):
            recommendations.append("修复核心组件导入问题，检查Python路径和模块结构")
        
        if not detailed_results.get("configurations", {}).get("success"):
            recommendations.append("完善配置文件，确保所有必需的配置文件存在")
        
        if not detailed_results.get("role_system", {}).get("success"):
            recommendations.append("修复角色系统初始化问题，检查角色文件格式")
        
        if not detailed_results.get("academic_scenario", {}).get("success"):
            recommendations.append("修复学术研究场景，确保所有组件正确初始化")
        
        if not detailed_results.get("expert_consultation", {}).get("success"):
            recommendations.append("修复专家咨询场景，检查专家数据库配置")
        
        if not detailed_results.get("file_system", {}).get("success"):
            recommendations.append("完善项目目录结构，确保所有必需目录存在")
        
        if not detailed_results.get("dependencies", {}).get("success"):
            recommendations.append("安装缺失的Python依赖包")
        
        if not recommendations:
            recommendations.append("✅ 系统验证全部通过，具备良好的工程可用性")
        
        return recommendations
    
    def save_validation_report(self, report: Dict[str, Any]):
        """保存验证报告"""
        try:
            report_path = Path("engineering_usability_validation_report.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n📊 验证报告已保存: {report_path}")
        except Exception as e:
            print(f"报告保存失败: {e}")
    
    def print_validation_summary(self, report: Dict[str, Any]):
        """打印验证摘要"""
        print("\n" + "=" * 80)
        print("📊 工程可用性验证报告")
        print("=" * 80)
        
        summary = report["validation_summary"]
        assessment = report["engineering_assessment"]
        
        print(f"验证时长: {summary['duration_seconds']:.1f} 秒")
        print(f"通过率: {summary['passed_checks']}/{summary['total_checks']} ({summary['passed_checks']/summary['total_checks']:.1%})")
        print(f"总体评分: {assessment['overall_score']:.1%}")
        
        print("\n🔧 工程质量评估:")
        print(f"  部署就绪: {'✅' if assessment['deployment_ready'] else '❌'}")
        print(f"  用户就绪: {'✅' if assessment['user_ready'] else '❌'}")
        print(f"  开发就绪: {'✅' if assessment['development_ready'] else '❌'}")
        
        print("\n💡 改进建议:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "=" * 80)


async def main():
    """主函数"""
    validator = EngineeringUsabilityValidator()
    report = await validator.run_validation()
    return report["validation_summary"]["passed_checks"] >= 5  # 至少5项通过


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)