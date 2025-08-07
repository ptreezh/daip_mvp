#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : validate_ddd_implementation.py
@Description:
    DDD implementation validation script.
    Validates that the implementation follows DDD principles and best practices.
"""

import asyncio
import importlib
import inspect
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Type
from dataclasses import dataclass, field

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationReport:
    """验证报告"""
    overall_score: float
    validations: List[ValidationResult]
    summary: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class DDDValidator:
    """DDD验证器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validation_results: List[ValidationResult] = []
        
        # DDD规则定义
        self.ddd_rules = {
            "layer_separation": {
                "description": "层级分离规则",
                "weight": 0.15,
                "check": self._check_layer_separation
            },
            "aggregates": {
                "description": "聚合根规则",
                "weight": 0.15,
                "check": self._check_aggregates
            },
            "repositories": {
                "description": "仓储模式规则",
                "weight": 0.10,
                "check": self._check_repositories
            },
            "domain_services": {
                "description": "领域服务规则",
                "weight": 0.10,
                "check": self._check_domain_services
            },
            "value_objects": {
                "description": "值对象规则",
                "weight": 0.10,
                "check": self._check_value_objects
            },
            "dependency_injection": {
                "description": "依赖注入规则",
                "weight": 0.10,
                "check": self._check_dependency_injection
            },
            "cqr_pattern": {
                "description": "CQRS模式规则",
                "weight": 0.10,
                "check": self._check_cqr_pattern
            },
            "use_cases": {
                "description": "用例规则",
                "weight": 0.10,
                "check": self._check_use_cases
            },
            "infrastructure": {
                "description": "基础设施规则",
                "weight": 0.10,
                "check": self._check_infrastructure
            }
        }
    
    async def validate_all(self) -> ValidationReport:
        """验证所有DDD规则"""
        self.logger.info("Starting DDD validation...")
        
        # 执行所有验证
        for rule_name, rule_config in self.ddd_rules.items():
            try:
                self.logger.info(f"Validating rule: {rule_name}")
                result = await rule_config["check"]()
                self.validation_results.append(result)
                
                if result.is_valid:
                    self.logger.info(f"PASS {rule_name}: {result.message}")
                else:
                    self.logger.warning(f"FAIL {rule_name}: {result.message}")
                    
            except Exception as e:
                error_result = ValidationResult(
                    is_valid=False,
                    message=f"Error validating {rule_name}: {str(e)}",
                    details={"error": str(e)}
                )
                self.validation_results.append(error_result)
                self.logger.error(f"Error validating {rule_name}: {e}")
        
        # 计算总分
        total_score = self._calculate_total_score()
        
        # 生成摘要
        summary = self._generate_summary()
        
        report = ValidationReport(
            overall_score=total_score,
            validations=self.validation_results,
            summary=summary
        )
        
        self.logger.info(f"DDD validation completed. Overall score: {total_score:.2f}")
        return report
    
    def _calculate_total_score(self) -> float:
        """计算总分"""
        total_weight = sum(rule_config["weight"] for rule_config in self.ddd_rules.values())
        weighted_score = 0
        
        for result, rule_config in zip(self.validation_results, self.ddd_rules.values()):
            weight = rule_config["weight"]
            score = 1.0 if result.is_valid else 0.0
            weighted_score += score * weight
        
        return weighted_score / total_weight
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成摘要"""
        total_rules = len(self.validation_results)
        passed_rules = sum(1 for result in self.validation_results if result.is_valid)
        failed_rules = total_rules - passed_rules
        
        # 按类型分类
        categories = {
            "architecture": ["layer_separation", "dependency_injection"],
            "domain": ["aggregates", "repositories", "domain_services", "value_objects"],
            "application": ["cqr_pattern", "use_cases"],
            "infrastructure": ["infrastructure"]
        }
        
        category_scores = {}
        for category, rule_names in categories.items():
            category_weight = sum(self.ddd_rules[rule_name]["weight"] for rule_name in rule_names)
            category_score = 0
            
            for rule_name in rule_names:
                for result in self.validation_results:
                    if rule_name in self.ddd_rules:
                        rule_weight = self.ddd_rules[rule_name]["weight"]
                        rule_score = 1.0 if result.is_valid else 0.0
                        category_score += rule_score * rule_weight
            
            category_scores[category] = category_score / category_weight if category_weight > 0 else 0
        
        return {
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "pass_rate": passed_rules / total_rules if total_rules > 0 else 0,
            "category_scores": category_scores,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        for result in self.validation_results:
            if not result.is_valid:
                if "layer_separation" in result.message:
                    recommendations.append("改进层级分离：确保领域层不依赖应用层和基础设施层")
                elif "aggregates" in result.message:
                    recommendations.append("完善聚合根设计：确保聚合边界清晰，一致性边界正确")
                elif "repositories" in result.message:
                    recommendations.append("实现仓储接口：确保仓储模式正确实现")
                elif "domain_services" in result.message:
                    recommendations.append("完善领域服务：确保业务逻辑在正确的层级")
                elif "value_objects" in result.message:
                    recommendations.append("使用值对象：将概念建模为值对象而非原始类型")
                elif "dependency_injection" in result.message:
                    recommendations.append("实现依赖注入：使用依赖注入容器管理依赖关系")
                elif "cqr_pattern" in result.message:
                    recommendations.append("完善CQRS模式：分离命令和查询操作")
                elif "use_cases" in result.message:
                    recommendations.append("完善用例设计：确保用例职责单一且清晰")
                elif "infrastructure" in result.message:
                    recommendations.append("完善基础设施：确保技术细节与领域逻辑分离")
        
        return list(set(recommendations))  # 去重
    
    async def _check_layer_separation(self) -> ValidationResult:
        """检查层级分离"""
        try:
            violations = []
            
            # 检查领域层是否依赖应用层
            domain_files = list(Path("src/domain").rglob("*.py"))
            for file_path in domain_files:
                content = file_path.read_text(encoding='utf-8')
                if "from src.application" in content or "from src.api" in content:
                    violations.append(f"领域层文件 {file_path} 依赖了应用层或API层")
            
            # 检查应用层是否依赖基础设施层
            app_files = list(Path("src/application").rglob("*.py"))
            for file_path in app_files:
                content = file_path.read_text(encoding='utf-8')
                if "from src.infrastructure" in content:
                    violations.append(f"应用层文件 {file_path} 直接依赖了基础设施层")
            
            is_valid = len(violations) == 0
            message = f"层级分离检查完成，发现 {len(violations)} 个违规"
            
            return ValidationResult(
                is_valid=is_valid,
                message=message,
                details={
                    "violations": violations,
                    "total_violations": len(violations)
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"层级分离检查失败: {str(e)}"
            )
    
    async def _check_aggregates(self) -> ValidationResult:
        """检查聚合根"""
        try:
            aggregates_found = 0
            aggregate_issues = []
            
            # 检查聚合根文件
            aggregates_file = Path("src/domain/aggregates.py")
            if aggregates_file.exists():
                content = aggregates_file.read_text(encoding='utf-8')
                
                # 检查是否有聚合根类
                if "class SessionAggregate" in content:
                    aggregates_found += 1
                if "class TaskAggregate" in content:
                    aggregates_found += 1
                if "class DebateAggregate" in content:
                    aggregates_found += 1
                
                # 检查聚合根是否包含必要的组件
                required_methods = ["add_task", "add_message", "create_debate"]
                for method in required_methods:
                    if f"def {method}" not in content:
                        aggregate_issues.append(f"聚合根缺少必要方法: {method}")
            
            is_valid = aggregates_found >= 3 and len(aggregate_issues) == 0
            message = f"聚合根检查完成，发现 {aggregates_found} 个聚合根"
            
            return ValidationResult(
                is_valid=is_valid,
                message=message,
                details={
                    "aggregates_found": aggregates_found,
                    "issues": aggregate_issues
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"聚合根检查失败: {str(e)}"
            )
    
    async def _check_repositories(self) -> ValidationResult:
        """检查仓储模式"""
        try:
            repositories_found = 0
            repository_issues = []
            
            # 检查仓储文件
            db_file = Path("src/infrastructure/database.py")
            if db_file.exists():
                content = db_file.read_text(encoding='utf-8')
                
                # 检查是否有仓储类
                repository_classes = [
                    "UserRepository", "SessionRepository", "TaskRepository",
                    "MessageRepository", "DebateRepository"
                ]
                
                for repo_class in repository_classes:
                    if f"class {repo_class}" in content:
                        repositories_found += 1
                    
                    # 检查是否有必要的方法
                    required_methods = ["create", "get_by_id", "update", "delete"]
                    for method in required_methods:
                        if f"async def {method}" not in content:
                            repository_issues.append(f"仓储 {repo_class} 缺少方法: {method}")
            
            is_valid = repositories_found >= 5 and len(repository_issues) == 0
            message = f"仓储模式检查完成，发现 {repositories_found} 个仓储"
            
            return ValidationResult(
                is_valid=is_valid,
                message=message,
                details={
                    "repositories_found": repositories_found,
                    "issues": repository_issues
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"仓储模式检查失败: {str(e)}"
            )
    
    async def _check_domain_services(self) -> ValidationResult:
        """检查领域服务"""
        try:
            services_found = 0
            service_issues = []
            
            # 检查领域服务文件
            services_file = Path("src/domain/domain_services.py")
            if services_file.exists():
                content = services_file.read_text(encoding='utf-8')
                
                # 检查是否有领域服务类
                service_classes = [
                    "EntranceSelectorService", "WorkflowOrchestratorService",
                    "UserInterventionService", "ConsensusTrackingService"
                ]
                
                for service_class in service_classes:
                    if f"class {service_class}" in content:
                        services_found += 1
                
                # 检查是否有异步方法
                if "async def" not in content:
                    service_issues.append("领域服务缺少异步方法")
            
            is_valid = services_found >= 4 and len(service_issues) == 0
            message = f"领域服务检查完成，发现 {services_found} 个服务"
            
            return ValidationResult(
                is_valid=is_valid,
                message=message,
                details={
                    "services_found": services_found,
                    "issues": service_issues
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"领域服务检查失败: {str(e)}"
            )
    
    async def _check_value_objects(self) -> ValidationResult:
        """检查值对象"""
        try:
            value_objects_found = 0
            vo_issues = []
            
            # 检查值对象文件
            vo_file = Path("src/domain/value_objects.py")
            if vo_file.exists():
                content = vo_file.read_text(encoding='utf-8')
                
                # 检查是否有值对象类
                vo_classes = [
                    "ConsensusLevel", "TimeInterval", "UserPreference",
                    "TaskPriority", "ResourceUsage"
                ]
                
                for vo_class in vo_classes:
                    if f"class {vo_class}" in content:
                        value_objects_found += 1
                
                # 检查是否是不可变的（frozen=True）
                if "frozen=True" not in content:
                    vo_issues.append("值对象应该标记为不可变（frozen=True）")
            
            is_valid = value_objects_found >= 5 and len(vo_issues) == 0
            message = f"值对象检查完成，发现 {value_objects_found} 个值对象"
            
            return ValidationResult(
                is_valid=is_valid,
                message=message,
                details={
                    "value_objects_found": value_objects_found,
                    "issues": vo_issues
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"值对象检查失败: {str(e)}"
            )
    
    async def _check_dependency_injection(self) -> ValidationResult:
        """检查依赖注入"""
        try:
            di_found = False
            di_issues = []
            
            # 检查应用层是否有依赖注入
            app_files = list(Path("src/application").rglob("*.py"))
            for file_path in app_files:
                content = file_path.read_text(encoding='utf-8')
                
                # 检查是否有构造函数注入
                if "__init__" in content and "def __init__" in content:
                    di_found = True
                
                # 检查是否有工厂模式
                if "Factory" in content:
                    di_found = True
            
            if not di_found:
                di_issues.append("未发现依赖注入模式")
            
            is_valid = di_found and len(di_issues) == 0
            message = f"依赖注入检查完成"
            
            return ValidationResult(
                is_valid=is_valid,
                message=message,
                details={
                    "dependency_injection_found": di_found,
                    "issues": di_issues
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"依赖注入检查失败: {str(e)}"
            )
    
    async def _check_cqr_pattern(self) -> ValidationResult:
        """检查CQRS模式"""
        try:
            cqr_found = False
            cqr_issues = []
            
            # 检查是否有命令和查询处理
            commands_file = Path("src/application/commands.py")
            queries_file = Path("src/application/queries.py")
            
            if commands_file.exists() and queries_file.exists():
                commands_content = commands_file.read_text(encoding='utf-8')
                queries_content = queries_file.read_text(encoding='utf-8')
                
                # 检查命令部分
                if "Command" in commands_content and "CommandHandler" in commands_content:
                    cqr_found = True
                else:
                    cqr_issues.append("命令模式实现不完整")
                
                # 检查查询部分
                if "Query" in queries_content and "QueryHandler" in queries_content:
                    cqr_found = True
                else:
                    cqr_issues.append("查询模式实现不完整")
                
                # 检查是否有总线
                if "CommandBus" in commands_content and "QueryBus" in queries_content:
                    cqr_found = True
                else:
                    cqr_issues.append("缺少命令总线或查询总线")
            else:
                cqr_issues.append("缺少命令或查询文件")
            
            is_valid = cqr_found and len(cqr_issues) == 0
            message = f"CQRS模式检查完成"
            
            return ValidationResult(
                is_valid=is_valid,
                message=message,
                details={
                    "cqr_pattern_found": cqr_found,
                    "issues": cqr_issues
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"CQRS模式检查失败: {str(e)}"
            )
    
    async def _check_use_cases(self) -> ValidationResult:
        """检查用例"""
        try:
            use_cases_found = 0
            use_case_issues = []
            
            # 检查用例文件
            use_cases_file = Path("src/application/use_cases.py")
            if use_cases_file.exists():
                content = use_cases_file.read_text(encoding='utf-8')
                
                # 检查是否有用例类
                use_case_classes = [
                    "CreateUserUseCase", "CreateSessionUseCase", "CreateTaskUseCase",
                    "ProcessMessageUseCase", "StartDebateUseCase"
                ]
                
                for use_case_class in use_case_classes:
                    if f"class {use_case_class}" in content:
                        use_cases_found += 1
                
                # 检查是否有execute方法
                if "async def execute" not in content:
                    use_case_issues.append("用例缺少execute方法")
            
            is_valid = use_cases_found >= 5 and len(use_case_issues) == 0
            message = f"用例检查完成，发现 {use_cases_found} 个用例"
            
            return ValidationResult(
                is_valid=is_valid,
                message=message,
                details={
                    "use_cases_found": use_cases_found,
                    "issues": use_case_issues
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"用例检查失败: {str(e)}"
            )
    
    async def _check_infrastructure(self) -> ValidationResult:
        """检查基础设施"""
        try:
            infra_found = 0
            infra_issues = []
            
            # 检查基础设施文件
            infra_files = [
                "src/infrastructure/database.py",
                "src/infrastructure/redis_client.py",
                "src/infrastructure/vector_store.py",
                "src/infrastructure/ollama_service.py"
            ]
            
            for file_path in infra_files:
                if Path(file_path).exists():
                    infra_found += 1
                else:
                    infra_issues.append(f"缺少基础设施文件: {file_path}")
            
            # 检查数据库连接
            db_file = Path("src/infrastructure/database.py")
            if db_file.exists():
                content = db_file.read_text(encoding='utf-8')
                if "DatabaseManager" not in content:
                    infra_issues.append("缺少数据库管理器")
            
            is_valid = infra_found >= 3 and len(infra_issues) == 0
            message = f"基础设施检查完成，发现 {infra_found} 个基础设施组件"
            
            return ValidationResult(
                is_valid=is_valid,
                message=message,
                details={
                    "infrastructure_components_found": infra_found,
                    "issues": infra_issues
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"基础设施检查失败: {str(e)}"
            )


async def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)
    
    print("DDD Implementation Validation")
    print("=" * 50)
    
    validator = DDDValidator()
    report = await validator.validate_all()
    
    # 输出结果
    print(f"\nOverall Score: {report.overall_score:.2f}")
    print(f"Passed: {report.summary['passed_rules']}")
    print(f"Failed: {report.summary['failed_rules']}")
    print(f"Pass Rate: {report.summary['pass_rate']:.2%}")
    
    print("\nCategory Scores:")
    for category, score in report.summary['category_scores'].items():
        print(f"  {category}: {score:.2f}")
    
    print("\nValidation Results:")
    for result in report.validations:
        status = "PASS" if result.is_valid else "FAIL"
        print(f"  {status} {result.message}")
        
        if result.details.get('violations'):
            for violation in result.details['violations']:
                print(f"    - {violation}")
    
    if report.summary['recommendations']:
        print("\nRecommendations:")
        for rec in report.summary['recommendations']:
            print(f"  - {rec}")
    
    # 保存报告
    report_file = "ddd_validation_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "overall_score": report.overall_score,
            "summary": report.summary,
            "validations": [
                {
                    "is_valid": r.is_valid,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in report.validations
            ],
            "timestamp": report.timestamp.isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    # 返回退出码
    return 0 if report.overall_score >= 0.8 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)