# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 13:00:00
@Author  : DAIP-LIVE Team
@File    : comprehensive_quality_validation_system.py
@Description:
    V0.3.9 Comprehensive Quality Validation System
    综合质量验证系统
"""

import asyncio
import json
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import inspect
import ast
import os
import sys
import re
from concurrent.futures import ThreadPoolExecutor
import hashlib
import uuid

from .performance_monitoring_system import PerformanceMonitoringSystem
from .enterprise_error_handling_system import EnterpriseErrorHandler, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """Quality metric types."""
    CODE_QUALITY = "code_quality"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    TEST_COVERAGE = "test_coverage"
    DOCUMENTATION = "documentation"
    COMPATIBILITY = "compatibility"


class ValidationLevel(Enum):
    """Validation levels."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    STRICT = "strict"


class QualityScore(Enum):
    """Quality score levels."""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"  # 80-89
    SATISFACTORY = "satisfactory"  # 70-79
    NEEDS_IMPROVEMENT = "needs_improvement"  # 60-69
    POOR = "poor"  # 0-59


@dataclass
class ValidationRule:
    """Validation rule definition."""
    rule_id: str
    name: str
    description: str
    metric: QualityMetric
    level: ValidationLevel
    weight: float
    condition: Callable[[Any], bool]
    message: str
    severity: ErrorSeverity = ErrorSeverity.MEDIUM


@dataclass
class ValidationResult:
    """Validation result."""
    rule_id: str
    passed: bool
    score: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QualityReport:
    """Quality report."""
    report_id: str
    timestamp: datetime
    validation_level: ValidationLevel
    overall_score: float
    quality_grade: QualityScore
    metric_scores: Dict[QualityMetric, float]
    validation_results: List[ValidationResult]
    recommendations: List[str]
    summary: Dict[str, Any]


class CodeQualityAnalyzer:
    """Code quality analyzer."""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> List[ValidationRule]:
        """Initialize validation rules."""
        return [
            ValidationRule(
                rule_id="CQ001",
                name="File Header Compliance",
                description="All Python files must have standardized headers",
                metric=QualityMetric.CODE_QUALITY,
                level=ValidationLevel.STANDARD,
                weight=1.0,
                condition=self._check_file_headers,
                message="Missing or incorrect file header",
                severity=ErrorSeverity.MEDIUM
            ),
            ValidationRule(
                rule_id="CQ002",
                name="Type Annotations",
                description="All functions must have complete type hints",
                metric=QualityMetric.CODE_QUALITY,
                level=ValidationLevel.STANDARD,
                weight=1.5,
                condition=self._check_type_annotations,
                message="Missing type annotations",
                severity=ErrorSeverity.MEDIUM
            ),
            ValidationRule(
                rule_id="CQ003",
                name="Docstring Coverage",
                description="All public functions must have docstrings",
                metric=QualityMetric.DOCUMENTATION,
                level=ValidationLevel.STANDARD,
                weight=1.2,
                condition=self._check_docstring_coverage,
                message="Missing docstrings",
                severity=ErrorSeverity.LOW
            ),
            ValidationRule(
                rule_id="CQ004",
                name="Code Complexity",
                description="Function complexity should be reasonable",
                metric=QualityMetric.MAINTAINABILITY,
                level=ValidationLevel.COMPREHENSIVE,
                weight=1.3,
                condition=self._check_code_complexity,
                message="High code complexity detected",
                severity=ErrorSeverity.MEDIUM
            ),
            ValidationRule(
                rule_id="CQ005",
                name="Line Length",
                description="Lines should not exceed 120 characters",
                metric=QualityMetric.CODE_QUALITY,
                level=ValidationLevel.BASIC,
                weight=0.8,
                condition=self._check_line_length,
                message="Line too long",
                severity=ErrorSeverity.LOW
            ),
            ValidationRule(
                rule_id="CQ006",
                name="Import Organization",
                description="Imports should be properly organized",
                metric=QualityMetric.CODE_QUALITY,
                level=ValidationLevel.STANDARD,
                weight=0.7,
                condition=self._check_import_organization,
                message="Import organization issues",
                severity=ErrorSeverity.LOW
            )
        ]
    
    def analyze_file(self, file_path: str) -> List[ValidationResult]:
        """Analyze a single file."""
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for rule in self.rules:
                try:
                    if rule.condition(content, file_path):
                        results.append(ValidationResult(
                            rule_id=rule.rule_id,
                            passed=True,
                            score=rule.weight,
                            message=f"✓ {rule.name}"
                        ))
                    else:
                        results.append(ValidationResult(
                            rule_id=rule.rule_id,
                            passed=False,
                            score=0.0,
                            message=f"✗ {rule.name}: {rule.message}",
                            details={"file": file_path}
                        ))
                except Exception as e:
                    results.append(ValidationResult(
                        rule_id=rule.rule_id,
                        passed=False,
                        score=0.0,
                        message=f"Error analyzing {rule.name}: {str(e)}",
                        details={"file": file_path, "error": str(e)}
                    ))
        
        except Exception as e:
            results.append(ValidationResult(
                rule_id="FILE_ERROR",
                passed=False,
                score=0.0,
                message=f"Error reading file {file_path}: {str(e)}"
            ))
        
        return results
    
    def _check_file_headers(self, content: str, file_path: str) -> bool:
        """Check file header compliance."""
        if not file_path.endswith('.py'):
            return True
        
        lines = content.split('\n')
        if len(lines) < 8:
            return False
        
        # Check for header pattern
        header_patterns = [
            r'# -*- coding: utf-8 -*-',
            r'"""',
            r'@Time\s*:\s*\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}:\d{2}',
            r'@Author\s*:\s*DAIP-LIVE Team',
            r'@File\s*:\s*.*\.py',
            r'@Description\s*:',
            r'"""'
        ]
        
        header_content = '\n'.join(lines[:8])
        for pattern in header_patterns:
            if not re.search(pattern, header_content, re.IGNORECASE):
                return False
        
        return True
    
    def _check_type_annotations(self, content: str, file_path: str) -> bool:
        """Check type annotations."""
        if not file_path.endswith('.py'):
            return True
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check return type annotation
                    if node.returns is None:
                        return False
                    
                    # Check argument annotations
                    for arg in node.args.args:
                        if arg.annotation is None:
                            return False
            
            return True
        
        except Exception:
            return False
    
    def _check_docstring_coverage(self, content: str, file_path: str) -> bool:
        """Check docstring coverage."""
        if not file_path.endswith('.py'):
            return True
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private methods
                    if node.name.startswith('_'):
                        continue
                    
                    # Check for docstring
                    if not (node.body and isinstance(node.body[0], ast.Expr) and 
                           isinstance(node.body[0].value, ast.Str)):
                        return False
            
            return True
        
        except Exception:
            return False
    
    def _check_code_complexity(self, content: str, file_path: str) -> bool:
        """Check code complexity."""
        if not file_path.endswith('.py'):
            return True
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > 10:  # Cyclomatic complexity threshold
                        return False
            
            return True
        
        except Exception:
            return False
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
        
        return complexity
    
    def _check_line_length(self, content: str, file_path: str) -> bool:
        """Check line length."""
        lines = content.split('\n')
        for line in lines:
            if len(line) > 120 and not line.strip().startswith('#'):
                return False
        return True
    
    def _check_import_organization(self, content: str, file_path: str) -> bool:
        """Check import organization."""
        if not file_path.endswith('.py'):
            return True
        
        lines = content.split('\n')
        import_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                import_lines.append(line)
        
        # Check if imports are grouped (standard library, third-party, local)
        standard_imports = []
        third_party_imports = []
        local_imports = []
        
        for imp in import_lines:
            if imp.startswith('import ') and not '.' in imp:
                standard_imports.append(imp)
            elif imp.startswith('from ') and any(imp.startswith(f'from {lib}') for lib in ['os', 'sys', 'json', 'time']):
                standard_imports.append(imp)
            elif any(pkg in imp for pkg in ['src', 'frontend', 'tests']):
                local_imports.append(imp)
            else:
                third_party_imports.append(imp)
        
        # Check ordering
        all_imports = standard_imports + third_party_imports + local_imports
        return all_imports == import_lines


class PerformanceValidator:
    """Performance validator."""
    
    def __init__(self, monitoring_system: PerformanceMonitoringSystem):
        self.monitoring_system = monitoring_system
    
    async def validate_performance(self) -> List[ValidationResult]:
        """Validate system performance."""
        results = []
        
        try:
            # Get performance metrics
            health = await self.monitoring_system.get_system_health()
            report = await self.monitoring_system.get_performance_report()
            
            # Validate system health
            if health.get("status") == "healthy":
                results.append(ValidationResult(
                    rule_id="PV001",
                    passed=True,
                    score=1.0,
                    message="✓ System health is good"
                ))
            else:
                results.append(ValidationResult(
                    rule_id="PV001",
                    passed=False,
                    score=0.0,
                    message=f"✗ System health is {health.get('status')}",
                    details={"health": health}
                ))
            
            # Validate resource usage
            if report and "performance_metrics" in report:
                metrics = report["performance_metrics"]
                
                # CPU usage validation
                cpu_usage = metrics.get("cpu_percent", 0)
                if cpu_usage < 80:
                    results.append(ValidationResult(
                        rule_id="PV002",
                        passed=True,
                        score=1.0,
                        message=f"✓ CPU usage is acceptable ({cpu_usage:.1f}%)"
                    ))
                else:
                    results.append(ValidationResult(
                        rule_id="PV002",
                        passed=False,
                        score=0.0,
                        message=f"✗ CPU usage is high ({cpu_usage:.1f}%)",
                        details={"cpu_usage": cpu_usage}
                    ))
                
                # Memory usage validation
                memory_usage = metrics.get("memory_percent", 0)
                if memory_usage < 85:
                    results.append(ValidationResult(
                        rule_id="PV003",
                        passed=True,
                        score=1.0,
                        message=f"✓ Memory usage is acceptable ({memory_usage:.1f}%)"
                    ))
                else:
                    results.append(ValidationResult(
                        rule_id="PV003",
                        passed=False,
                        score=0.0,
                        message=f"✗ Memory usage is high ({memory_usage:.1f}%)",
                        details={"memory_usage": memory_usage}
                    ))
            
            # Validate optimization recommendations
            if report and "recommendations" in report:
                recommendations = report["recommendations"]
                if len(recommendations) < 3:
                    results.append(ValidationResult(
                        rule_id="PV004",
                        passed=True,
                        score=1.0,
                        message=f"✓ Few optimization recommendations ({len(recommendations)})"
                    ))
                else:
                    results.append(ValidationResult(
                        rule_id="PV004",
                        passed=False,
                        score=0.0,
                        message=f"✗ Many optimization recommendations ({len(recommendations)})",
                        details={"recommendations": recommendations}
                    ))
        
        except Exception as e:
            results.append(ValidationResult(
                rule_id="PV_ERROR",
                passed=False,
                score=0.0,
                message=f"Performance validation error: {str(e)}"
            ))
        
        return results


class SecurityValidator:
    """Security validator."""
    
    def __init__(self):
        self.security_rules = self._initialize_security_rules()
    
    def _initialize_security_rules(self) -> List[ValidationRule]:
        """Initialize security rules."""
        return [
            ValidationRule(
                rule_id="SEC001",
                name="Hardcoded Secrets",
                description="No hardcoded secrets or passwords",
                metric=QualityMetric.SECURITY,
                level=ValidationLevel.STRICT,
                weight=2.0,
                condition=self._check_hardcoded_secrets,
                message="Hardcoded secrets detected",
                severity=ErrorSeverity.CRITICAL
            ),
            ValidationRule(
                rule_id="SEC002",
                name="SQL Injection",
                description="Prevent SQL injection vulnerabilities",
                metric=QualityMetric.SECURITY,
                level=ValidationLevel.STRICT,
                weight=2.0,
                condition=self._check_sql_injection,
                message="SQL injection vulnerability detected",
                severity=ErrorSeverity.CRITICAL
            ),
            ValidationRule(
                rule_id="SEC003",
                name="Input Validation",
                description="Input should be properly validated",
                metric=QualityMetric.SECURITY,
                level=ValidationLevel.STANDARD,
                weight=1.5,
                condition=self._check_input_validation,
                message="Input validation issues detected",
                severity=ErrorSeverity.HIGH
            )
        ]
    
    def validate_security(self, file_paths: List[str]) -> List[ValidationResult]:
        """Validate security."""
        results = []
        
        for file_path in file_paths:
            if not file_path.endswith('.py'):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for rule in self.security_rules:
                    try:
                        if rule.condition(content, file_path):
                            results.append(ValidationResult(
                                rule_id=rule.rule_id,
                                passed=True,
                                score=rule.weight,
                                message=f"✓ {rule.name} ({file_path})"
                            ))
                        else:
                            results.append(ValidationResult(
                                rule_id=rule.rule_id,
                                passed=False,
                                score=0.0,
                                message=f"✗ {rule.name} ({file_path}): {rule.message}",
                                details={"file": file_path}
                            ))
                    except Exception as e:
                        results.append(ValidationResult(
                            rule_id=rule.rule_id,
                            passed=False,
                            score=0.0,
                            message=f"Error checking {rule.name}: {str(e)}",
                            details={"file": file_path, "error": str(e)}
                        ))
            
            except Exception as e:
                results.append(ValidationResult(
                    rule_id="SEC_FILE_ERROR",
                    passed=False,
                    score=0.0,
                    message=f"Error reading file {file_path}: {str(e)}"
                ))
        
        return results
    
    def _check_hardcoded_secrets(self, content: str, file_path: str) -> bool:
        """Check for hardcoded secrets."""
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'secret\s*=\s*["\'][^"\']{8,}["\']',
            r'api_key\s*=\s*["\'][^"\']{8,}["\']',
            r'token\s*=\s*["\'][^"\']{8,}["\']',
            r'private_key\s*=\s*["\'][^"\']{8,}["\']'
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        
        return True
    
    def _check_sql_injection(self, content: str, file_path: str) -> bool:
        """Check for SQL injection vulnerabilities."""
        injection_patterns = [
            r'execute\s*\(\s*["\'].*%.*["\']',
            r'execute\s*\(\s*["\'].*\+.*["\']',
            r'execute\s*\(\s*["\'].*format\s*\(.*["\']',
            r'cursor\.execute\s*\(\s*f["\']',
            r'cursor\.execute\s*\(\s*["\'].*%.*["\']'
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        
        return True
    
    def _check_input_validation(self, content: str, file_path: str) -> bool:
        """Check input validation."""
        # Look for input validation patterns
        validation_patterns = [
            r'validate_input',
            r'sanitize_input',
            r'isinstance\s*\(',
            r'type\s*\(',
            r're\.match\s*\(',
            r're\.search\s*\('
        ]
        
        has_validation = any(re.search(pattern, content, re.IGNORECASE) for pattern in validation_patterns)
        
        # If there are user input functions, validation should be present
        input_patterns = [
            r'input\s*\(',
            r'request\.get',
            r'request\.post',
            r'form\.get',
            r'args\.get'
        ]
        
        has_input = any(re.search(pattern, content, re.IGNORECASE) for pattern in input_patterns)
        
        return not has_input or has_validation


class ComprehensiveQualityValidator:
    """Comprehensive quality validator."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.code_analyzer = CodeQualityAnalyzer()
        self.performance_validator = None
        self.security_validator = SecurityValidator()
        self.error_handler = None
        self.validation_history: List[QualityReport] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def initialize(self, monitoring_system: PerformanceMonitoringSystem, error_handler: EnterpriseErrorHandler):
        """Initialize validator with dependencies."""
        self.performance_validator = PerformanceValidator(monitoring_system)
        self.error_handler = error_handler
    
    async def validate_system(self, level: ValidationLevel = ValidationLevel.STANDARD) -> QualityReport:
        """Validate entire system."""
        logger.info(f"Starting comprehensive quality validation at level: {level.value}")
        
        start_time = time.time()
        report_id = str(uuid.uuid4())
        
        # Collect Python files
        python_files = self._collect_python_files()
        
        # Run validations
        validation_results = []
        
        # Code quality validation
        code_results = await self._validate_code_quality(python_files, level)
        validation_results.extend(code_results)
        
        # Performance validation
        if self.performance_validator:
            perf_results = await self.performance_validator.validate_performance()
            validation_results.extend(perf_results)
        
        # Security validation
        security_results = self.security_validator.validate_security(python_files)
        validation_results.extend(security_results)
        
        # Error handling validation
        if self.error_handler:
            error_results = self._validate_error_handling()
            validation_results.extend(error_results)
        
        # Calculate scores
        metric_scores = self._calculate_metric_scores(validation_results)
        overall_score = self._calculate_overall_score(metric_scores)
        quality_grade = self._determine_quality_grade(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(validation_results, metric_scores)
        
        # Create report
        report = QualityReport(
            report_id=report_id,
            timestamp=datetime.now(),
            validation_level=level,
            overall_score=overall_score,
            quality_grade=quality_grade,
            metric_scores=metric_scores,
            validation_results=validation_results,
            recommendations=recommendations,
            summary={
                "total_files": len(python_files),
                "total_validations": len(validation_results),
                "passed_validations": len([r for r in validation_results if r.passed]),
                "validation_duration": time.time() - start_time
            }
        )
        
        # Store report
        self.validation_history.append(report)
        
        logger.info(f"Quality validation completed: {overall_score:.1f}% ({quality_grade.value})")
        return report
    
    def _collect_python_files(self) -> List[str]:
        """Collect Python files for validation."""
        python_files = []
        
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    async def _validate_code_quality(self, python_files: List[str], level: ValidationLevel) -> List[ValidationResult]:
        """Validate code quality."""
        results = []
        
        # Filter rules by validation level
        applicable_rules = [r for r in self.code_analyzer.rules if r.level.value <= level.value]
        
        # Analyze files in parallel
        tasks = []
        for file_path in python_files:
            task = asyncio.get_event_loop().run_in_executor(
                self.executor, self.code_analyzer.analyze_file, file_path
            )
            tasks.append(task)
        
        file_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for file_result in file_results:
            if isinstance(file_result, Exception):
                results.append(ValidationResult(
                    rule_id="CODE_ANALYSIS_ERROR",
                    passed=False,
                    score=0.0,
                    message=f"Code analysis error: {str(file_result)}"
                ))
            else:
                # Filter results by applicable rules
                filtered_results = [r for r in file_result if any(r.rule_id == rule.rule_id for rule in applicable_rules)]
                results.extend(filtered_results)
        
        return results
    
    def _validate_error_handling(self) -> List[ValidationResult]:
        """Validate error handling."""
        results = []
        
        if not self.error_handler:
            return results
        
        # Get error statistics
        stats = self.error_handler.get_error_statistics()
        
        # Validate error rates
        total_errors = stats.get("total_errors", 0)
        if total_errors < 10:
            results.append(ValidationResult(
                rule_id="EH001",
                passed=True,
                score=1.0,
                message=f"✓ Low error rate ({total_errors} errors)"
            ))
        else:
            results.append(ValidationResult(
                rule_id="EH001",
                passed=False,
                score=0.0,
                message=f"✗ High error rate ({total_errors} errors)",
                details={"total_errors": total_errors}
            ))
        
        # Validate recovery success rate
        recovery_stats = stats.get("recovery_statistics", {})
        success_rate = recovery_stats.get("success_rate", 0)
        if success_rate > 80:
            results.append(ValidationResult(
                rule_id="EH002",
                passed=True,
                score=1.0,
                message=f"✓ Good recovery success rate ({success_rate:.1f}%)"
            ))
        else:
            results.append(ValidationResult(
                rule_id="EH002",
                passed=False,
                score=0.0,
                message=f"✗ Low recovery success rate ({success_rate:.1f}%)",
                details={"success_rate": success_rate}
            ))
        
        return results
    
    def _calculate_metric_scores(self, validation_results: List[ValidationResult]) -> Dict[QualityMetric, float]:
        """Calculate scores for each quality metric."""
        metric_scores = {}
        
        # Group results by metric
        metric_results = {}
        for result in validation_results:
            # Find the rule for this result
            rule = None
            for r in self.code_analyzer.rules + self.security_validator.security_rules:
                if r.rule_id == result.rule_id:
                    rule = r
                    break
            
            if rule:
                metric = rule.metric
                if metric not in metric_results:
                    metric_results[metric] = []
                metric_results[metric].append((result.score, rule.weight))
        
        # Calculate weighted scores
        for metric, results in metric_results.items():
            if results:
                total_weight = sum(weight for _, weight in results)
                weighted_score = sum(score * weight for score, weight in results)
                metric_scores[metric] = (weighted_score / total_weight) * 100
            else:
                metric_scores[metric] = 100.0  # Default score if no validations
        
        return metric_scores
    
    def _calculate_overall_score(self, metric_scores: Dict[QualityMetric, float]) -> float:
        """Calculate overall quality score."""
        if not metric_scores:
            return 0.0
        
        # Calculate weighted average
        weights = {
            QualityMetric.CODE_QUALITY: 1.5,
            QualityMetric.PERFORMANCE: 1.2,
            QualityMetric.RELIABILITY: 1.3,
            QualityMetric.SECURITY: 2.0,
            QualityMetric.MAINTAINABILITY: 1.1,
            QualityMetric.TEST_COVERAGE: 1.0,
            QualityMetric.DOCUMENTATION: 0.8,
            QualityMetric.COMPATIBILITY: 0.6
        }
        
        total_weight = 0.0
        weighted_score = 0.0
        
        for metric, score in metric_scores.items():
            weight = weights.get(metric, 1.0)
            total_weight += weight
            weighted_score += score * weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_grade(self, score: float) -> QualityScore:
        """Determine quality grade from score."""
        if score >= 90:
            return QualityScore.EXCELLENT
        elif score >= 80:
            return QualityScore.GOOD
        elif score >= 70:
            return QualityScore.SATISFACTORY
        elif score >= 60:
            return QualityScore.NEEDS_IMPROVEMENT
        else:
            return QualityScore.POOR
    
    def _generate_recommendations(self, validation_results: List[ValidationResult], metric_scores: Dict[QualityMetric, float]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Analyze failed validations
        failed_results = [r for r in validation_results if not r.passed]
        if failed_results:
            recommendations.append(f"修复 {len(failed_results)} 个失败的验证项目")
        
        # Analyze metric scores
        low_metrics = [(metric, score) for metric, score in metric_scores.items() if score < 70]
        if low_metrics:
            for metric, score in low_metrics:
                recommendations.append(f"改进 {metric.value} 质量 (当前分数: {score:.1f}%)")
        
        # General recommendations
        if metric_scores.get(QualityMetric.SECURITY, 100) < 90:
            recommendations.append("加强安全性检查和代码审查")
        
        if metric_scores.get(QualityMetric.PERFORMANCE, 100) < 80:
            recommendations.append("优化系统性能和资源使用")
        
        if metric_scores.get(QualityMetric.CODE_QUALITY, 100) < 80:
            recommendations.append("提高代码质量，遵循编码规范")
        
        if metric_scores.get(QualityMetric.DOCUMENTATION, 100) < 70:
            recommendations.append("完善文档和注释")
        
        return recommendations
    
    def get_validation_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get validation history."""
        cutoff_time = datetime.now() - timedelta(days=days)
        return [
            {
                "report_id": report.report_id,
                "timestamp": report.timestamp.isoformat(),
                "overall_score": report.overall_score,
                "quality_grade": report.quality_grade.value,
                "validation_level": report.validation_level.value
            }
            for report in self.validation_history
            if report.timestamp >= cutoff_time
        ]
    
    def export_quality_report(self, report: QualityReport, filename: str = "quality_report.json") -> bool:
        """Export quality report to file."""
        try:
            export_data = {
                "report_id": report.report_id,
                "timestamp": report.timestamp.isoformat(),
                "validation_level": report.validation_level.value,
                "overall_score": report.overall_score,
                "quality_grade": report.quality_grade.value,
                "metric_scores": {metric.value: score for metric, score in report.metric_scores.items()},
                "summary": report.summary,
                "recommendations": report.recommendations,
                "validation_results": [
                    {
                        "rule_id": result.rule_id,
                        "passed": result.passed,
                        "score": result.score,
                        "message": result.message,
                        "timestamp": result.timestamp.isoformat()
                    }
                    for result in report.validation_results
                ]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Quality report exported to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export quality report: {e}")
            return False


# Global instance
_comprehensive_quality_validator: Optional[ComprehensiveQualityValidator] = None


def get_comprehensive_quality_validator() -> ComprehensiveQualityValidator:
    """Get global comprehensive quality validator instance."""
    global _comprehensive_quality_validator
    if _comprehensive_quality_validator is None:
        config = {
            "validation_levels": {
                "basic": {"timeout": 300, "max_files": 100},
                "standard": {"timeout": 600, "max_files": 500},
                "comprehensive": {"timeout": 1200, "max_files": 1000},
                "strict": {"timeout": 1800, "max_files": 2000}
            }
        }
        _comprehensive_quality_validator = ComprehensiveQualityValidator(config)
    return _comprehensive_quality_validator


def initialize_comprehensive_quality_validator(config: Dict[str, Any]):
    """Initialize comprehensive quality validator."""
    global _comprehensive_quality_validator
    _comprehensive_quality_validator = ComprehensiveQualityValidator(config)