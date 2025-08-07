#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 10:00:00
@Author  : DAIP-LIVE Team
@File    : mandatory_rules_checker.py
@Description:
    Enforces mandatory development rules before allowing commits or builds.
    This script checks all critical rules defined in CLAUDE.md.
"""

import sys
import subprocess
import os
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any
import json
from datetime import datetime


class MandatoryRulesChecker:
    """Enforces all mandatory development rules"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"
        self.violations = []
        self.warnings = []
        
    def log_violation(self, rule: str, message: str, severity: str = "ERROR"):
        """Log a rule violation"""
        violation = {
            "rule": rule,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        self.violations.append(violation)
        print(f"[VIOLATION] {severity}: {rule} - {message}")
        
    def log_warning(self, rule: str, message: str):
        """Log a warning"""
        warning = {
            "rule": rule,
            "message": message,
            "severity": "WARNING",
            "timestamp": datetime.now().isoformat()
        }
        self.warnings.append(warning)
        print(f"[WARNING] {rule} - {message}")
        
    def run_command(self, command: List[str], cwd: Path = None) -> Tuple[bool, str]:
        """Run a command and return success status and output"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Command failed: {e}"
            
    def check_code_quality_gates(self):
        """Rule 1: Code Quality Gates"""
        print("[CHECK] Code Quality Gates...")
        
        # Check Black formatting
        success, output = self.run_command(["black", "--check", "src/", "tests/"])
        if not success:
            self.log_violation(
                "Code Quality Gates",
                "Black formatting check failed. Run: black src/ tests/",
                "CRITICAL"
            )
            
        # Check Ruff linting
        success, output = self.run_command(["ruff", "check", "src/", "tests/"])
        if not success:
            self.log_violation(
                "Code Quality Gates",
                "Ruff linting failed. Fix issues before committing.",
                "CRITICAL"
            )
            
        # Check MyPy type checking
        success, output = self.run_command(["mypy", "src/"])
        if not success:
            self.log_violation(
                "Code Quality Gates",
                "MyPy type checking failed. All type hints must be correct.",
                "CRITICAL"
            )
            
    def check_file_headers(self):
        """Rule 2: File Headers MANDATORY"""
        print("[CHECK] File Headers...")
        
        for py_file in self.src_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for basic header elements
                has_encoding = "# -*- coding: utf-8 -*-" in content
                has_author = "@Author  : DAIP-LIVE Team" in content
                has_description = "@Description:" in content
                
                if not (has_encoding and has_author and has_description):
                    self.log_violation(
                        "File Headers MANDATORY",
                        f"Missing or invalid header in {py_file.relative_to(self.project_root)}",
                        "CRITICAL"
                    )
                    
            except Exception as e:
                self.log_warning(
                    "File Headers MANDATORY",
                    f"Could not read {py_file}: {e}"
                )
                
    def check_pre_commit_config(self):
        """Rule 5: Pre-commit Hooks"""
        print("[CHECK] Pre-commit Configuration...")
        
        pre_commit_file = self.project_root / ".pre-commit-config.yaml"
        if not pre_commit_file.exists():
            self.log_violation(
                "Pre-commit Hooks",
                "Missing .pre-commit-config.yaml file",
                "CRITICAL"
            )
            
    def check_architecture_compliance(self):
        """Rule 6: Architecture Compliance"""
        print("[CHECK] Architecture Compliance...")
        
        # Check for proper directory structure
        required_dirs = [
            "src/core_services",
            "src/institutional_primitives", 
            "src/virtual_role_chat",
            "src/kernel",
            "src/api",
            "src/cli"
        ]
        
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                self.log_violation(
                    "Architecture Compliance",
                    f"Missing required directory: {dir_path}",
                    "CRITICAL"
                )
                
    def check_python_version(self):
        """Rule 10: Environment Standards"""
        print("[CHECK] Python Version...")
        
        if sys.version_info < (3, 10):
            self.log_violation(
                "Environment Standards",
                f"Python 3.10+ required, found {sys.version_info.major}.{sys.version_info.minor}",
                "CRITICAL"
            )
            
    def check_poetry_dependencies(self):
        """Rule 10: Poetry Dependencies"""
        print("[CHECK] Poetry Configuration...")
        
        if not (self.project_root / "pyproject.toml").exists():
            self.log_violation(
                "Environment Standards",
                "Missing pyproject.toml file",
                "CRITICAL"
            )
            
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report"""
        critical_violations = [v for v in self.violations if v["severity"] in ["CRITICAL", "ERROR"]]
        warnings = self.warnings
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_violations": len(self.violations),
            "critical_violations": len(critical_violations),
            "warnings": len(warnings),
            "pass": len(critical_violations) == 0,
            "violations": self.violations,
            "warnings": self.warnings,
            "summary": {
                "status": "PASS" if len(critical_violations) == 0 else "FAIL",
                "message": "All mandatory rules passed" if len(critical_violations) == 0 else f"{len(critical_violations)} critical violations found"
            }
        }
        
        return report
        
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all mandatory rule checks"""
        print("[MANDATORY RULES] Starting Mandatory Rules Check...")
        print("=" * 60)
        
        self.check_code_quality_gates()
        self.check_file_headers()
        self.check_pre_commit_config()
        self.check_architecture_compliance()
        self.check_python_version()
        self.check_poetry_dependencies()
        
        print("=" * 60)
        
        report = self.generate_report()
        
        # Print summary
        if report["pass"]:
            print("[SUCCESS] ALL MANDATORY RULES PASSED")
        else:
            print(f"[FAIL] {report['critical_violations']} CRITICAL VIOLATIONS FOUND")
            print("Fix all critical violations before committing")
            
        if report["warnings"]:
            print(f"[INFO] {report['warnings']} warnings found")
            
        return report


def main():
    """Main entry point"""
    checker = MandatoryRulesChecker()
    report = checker.run_all_checks()
    
    # Save report to file
    report_file = Path("mandatory_rules_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"\n[REPORT] Report saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()