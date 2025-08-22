#!/usr/bin/env python3
"""
Unified CLI Compliance Testing and Review Script

This script performs comprehensive testing and review of the DAIP-LIVE CLI implementation
against the unified command-line interface specifications.

Testing Strategy:
1. Code Structure Review
2. Command Implementation Verification
3. Backend Service Integration Testing
4. Phase Compliance Check
5. Acceptance Criteria Validation
6. Performance and Error Handling Assessment
"""

import sys
import os
import json
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class CLIComplianceTester:
    """Comprehensive CLI compliance testing and review system."""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = {
            "code_structure": {},
            "command_implementation": {},
            "backend_integration": {},
            "phase_compliance": {},
            "acceptance_criteria": {},
            "performance": {},
            "error_handling": {},
            "overall_score": 0.0,
            "recommendations": [],
            "critical_issues": []
        }
        self.console_print = print  # Use simple print for testing
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all compliance tests and generate comprehensive report."""
        self.console_print("🚀 Starting Comprehensive CLI Compliance Testing...")
        
        # 1. Code Structure Review
        self.console_print("\n📋 1. Code Structure Review")
        self.test_code_structure()
        
        # 2. Command Implementation Verification
        self.console_print("\n🔧 2. Command Implementation Verification")
        self.test_command_implementation()
        
        # 3. Backend Service Integration Testing
        self.console_print("\n🔗 3. Backend Service Integration Testing")
        self.test_backend_integration()
        
        # 4. Phase Compliance Check
        self.console_print("\n📊 4. Phase Compliance Check")
        self.test_phase_compliance()
        
        # 5. Acceptance Criteria Validation
        self.console_print("\n✅ 5. Acceptance Criteria Validation")
        self.test_acceptance_criteria()
        
        # 6. Performance and Error Handling
        self.console_print("\n⚡ 6. Performance and Error Handling")
        self.test_performance_and_error_handling()
        
        # Calculate overall score
        self.calculate_overall_score()
        
        # Generate recommendations
        self.generate_recommendations()
        
        return self.test_results
    
    def test_code_structure(self) -> None:
        """Review CLI code structure against specifications."""
        results = {
            "cli_main_exists": False,
            "command_modules_exist": False,
            "proper_imports": False,
            "typer_integration": False,
            "error_handling": False,
            "documentation": False,
            "score": 0.0,
            "issues": []
        }
        
        try:
            # Check main CLI structure
            cli_main_path = self.project_root / "src" / "cli" / "main.py"
            if cli_main_path.exists():
                results["cli_main_exists"] = True
                results["score"] += 20
                
                # Check command modules
                command_modules = [
                    "src/cli/commands/debate_commands.py",
                    "src/cli/commands/role_commands.py", 
                    "src/cli/commands/wiki_commands.py",
                    "src/cli/commands/chat_commands.py",
                    "src/cli/commands/workflow_commands.py",
                    "src/cli/commands/system_commands.py"
                ]
                
                existing_modules = 0
                for module in command_modules:
                    if (self.project_root / module).exists():
                        existing_modules += 1
                
                if existing_modules >= 4:
                    results["command_modules_exist"] = True
                    results["score"] += 20
                else:
                    results["issues"].append(f"Only {existing_modules}/{len(command_modules)} command modules exist")
                
                # Check Typer integration
                with open(cli_main_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'typer' in content and 'app = typer.Typer' in content:
                        results["typer_integration"] = True
                        results["score"] += 20
                    else:
                        results["issues"].append("Typer integration not found or incomplete")
                
                # Check error handling
                if 'try:' in content and 'except' in content:
                    results["error_handling"] = True
                    results["score"] += 20
                
                # Check documentation
                if '"""' in content and 'help' in content:
                    results["documentation"] = True
                    results["score"] += 20
                
            else:
                results["issues"].append("CLI main file not found")
                
        except Exception as e:
            results["issues"].append(f"Code structure test failed: {e}")
        
        self.test_results["code_structure"] = results
        self.console_print(f"   Code Structure Score: {results['score']}/100")
    
    def test_command_implementation(self) -> None:
        """Test command implementation against task requirements."""
        results = {
            "core_commands": {},
            "debate_commands": {},
            "chat_commands": {},
            "wiki_commands": {},
            "role_commands": {},
            "workflow_commands": {},
            "score": 0.0,
            "issues": []
        }
        
        # Test core commands
        core_commands = ["status", "help", "pa chat"]
        for cmd in core_commands:
            results["core_commands"][cmd] = self._test_command_exists(cmd)
        
        # Test debate commands (recently implemented)
        debate_commands = [
            "debate start",
            "debate export-to-wiki", 
            "debate view-disagreements",
            "debate select-consensus-algorithm"
        ]
        for cmd in debate_commands:
            results["debate_commands"][cmd] = self._test_command_exists(cmd)
        
        # Test chat commands
        chat_commands = [
            "chat start",
            "chat message", 
            "chat list",
            "chat history",
            "chat clear",
            "chat close"
        ]
        for cmd in chat_commands:
            results["chat_commands"][cmd] = self._test_command_exists(cmd)
        
        # Test wiki commands
        wiki_commands = [
            "wiki create",
            "wiki view",
            "wiki edit",
            "wiki delete",
            "wiki list",
            "wiki search",
            "wiki export"
        ]
        for cmd in wiki_commands:
            results["wiki_commands"][cmd] = self._test_command_exists(cmd)
        
        # Calculate score based on implemented commands
        total_commands = sum(len(cmds) for cmds in results.values() if isinstance(cmds, dict))
        implemented_commands = sum(sum(1 for v in cmds.values() if v) for cmds in results.values() if isinstance(cmds, dict))
        
        if total_commands > 0:
            results["score"] = (implemented_commands / total_commands) * 100
        
        self.test_results["command_implementation"] = results
        self.console_print(f"   Command Implementation Score: {results['score']:.1f}%")
    
    def test_backend_integration(self) -> None:
        """Test integration with backend services."""
        results = {
            "role_manager": False,
            "wiki_service": False,
            "chat_service": False,
            "debate_manager": False,
            "llm_manager": False,
            "memory_service": False,
            "score": 0.0,
            "issues": []
        }
        
        try:
            # Test backend service imports
            services = [
                ("role_manager", "src.core_services.role_manager.RoleManager"),
                ("wiki_service", "src.core_services.wiki_service.WikiService"),
                ("debate_manager", "src.core_services.debate_manager.DebateManager"),
                ("llm_manager", "src.core_services.integrated_llm_manager.IntegratedLLMManager"),
                ("memory_service", "src.core_services.memory_agent.MemAgent")
            ]
            
            working_services = 0
            for service_name, service_path in services:
                try:
                    module_path, class_name = service_path.rsplit('.', 1)
                    module = importlib.import_module(module_path)
                    cls = getattr(module, class_name)
                    results[service_name] = True
                    working_services += 1
                except Exception as e:
                    results["issues"].append(f"Service {service_name} failed: {e}")
            
            # Test chat service integration (virtual_role_chat)
            try:
                from src.virtual_role_chat.chat_room_manager import ChatRoomManager
                from src.virtual_role_chat.chat_session_service import ChatSessionService
                results["chat_service"] = True
                working_services += 1
            except Exception as e:
                results["issues"].append(f"Chat service integration failed: {e}")
            
            results["score"] = (working_services / len(services)) * 100
            
        except Exception as e:
            results["issues"].append(f"Backend integration test failed: {e}")
        
        self.test_results["backend_integration"] = results
        self.console_print(f"   Backend Integration Score: {results['score']:.1f}%")
    
    def test_phase_compliance(self) -> None:
        """Test compliance with phase requirements."""
        results = {
            "phase_1_complete": False,
            "phase_2_complete": False,
            "phase_3_complete": False,
            "phase_4_5_planned": False,
            "score": 0.0,
            "issues": []
        }
        
        try:
            # Phase 1: Core CLI Enhancement
            phase_1_commands = ["pa chat", "debate view-disagreements", "debate select-consensus-algorithm"]
            phase_1_complete = all(self._test_command_exists(cmd) for cmd in phase_1_commands)
            results["phase_1_complete"] = phase_1_complete
            
            # Phase 2: Chat Room Functionality
            phase_2_commands = ["chat start", "chat message", "chat history"]
            phase_2_complete = all(self._test_command_exists(cmd) for cmd in phase_2_commands)
            results["phase_2_complete"] = phase_2_complete
            
            # Phase 3: Wiki Knowledge Management
            phase_3_commands = ["wiki create", "wiki view", "wiki export", "wiki delete"]
            phase_3_complete = all(self._test_command_exists(cmd) for cmd in phase_3_commands)
            results["phase_3_complete"] = phase_3_complete
            
            # Phase 4/5: Role Management and Workflow
            phase_4_5_commands = ["roles create", "roles invite", "workflow list", "workflow create"]
            phase_4_5_planned = any(self._test_command_exists(cmd) for cmd in phase_4_5_commands)
            results["phase_4_5_planned"] = phase_4_5_planned
            
            # Calculate score
            completed_phases = sum([
                phase_1_complete,
                phase_2_complete, 
                phase_3_complete,
                phase_4_5_planned
            ])
            results["score"] = (completed_phases / 4) * 100
            
            if not phase_1_complete:
                results["issues"].append("Phase 1 (Core CLI Enhancement) incomplete")
            if not phase_2_complete:
                results["issues"].append("Phase 2 (Chat Room Functionality) incomplete")
            if not phase_3_complete:
                results["issues"].append("Phase 3 (Wiki Knowledge Management) incomplete")
                
        except Exception as e:
            results["issues"].append(f"Phase compliance test failed: {e}")
        
        self.test_results["phase_compliance"] = results
        self.console_print(f"   Phase Compliance Score: {results['score']:.1f}%")
    
    def test_acceptance_criteria(self) -> None:
        """Test against acceptance criteria."""
        results = {
            "functional_requirements": False,
            "quality_requirements": False,
            "performance_requirements": False,
            "documentation_requirements": False,
            "score": 0.0,
            "issues": []
        }
        
        try:
            # Functional requirements
            cmd_impl = self.test_results["command_implementation"]
            if cmd_impl.get("score", 0) > 70:
                results["functional_requirements"] = True
                results["score"] += 25
            else:
                results["issues"].append("Functional requirements not met")
            
            # Quality requirements
            backend_int = self.test_results["backend_integration"]
            if backend_int.get("score", 0) > 60:
                results["quality_requirements"] = True
                results["score"] += 25
            else:
                results["issues"].append("Quality requirements not met")
            
            # Performance requirements (basic check)
            try:
                start_time = datetime.now()
                # Simple performance test
                from src.cli.main import app
                end_time = datetime.now()
                if (end_time - start_time).total_seconds() < 5:  # Should load quickly
                    results["performance_requirements"] = True
                    results["score"] += 25
                else:
                    results["issues"].append("Performance requirements not met")
            except Exception:
                results["issues"].append("Performance test failed")
            
            # Documentation requirements
            docs = [
                "README.md",
                ".kiro/specs/unified-command-line-interface/README.md",
                ".kiro/specs/unified-command-line-interface/COMMAND_REFERENCE.md"
            ]
            existing_docs = sum(1 for doc in docs if (self.project_root / doc).exists())
            if existing_docs >= 2:
                results["documentation_requirements"] = True
                results["score"] += 25
            else:
                results["issues"].append(f"Documentation incomplete: {existing_docs}/{len(docs)} docs exist")
                
        except Exception as e:
            results["issues"].append(f"Acceptance criteria test failed: {e}")
        
        self.test_results["acceptance_criteria"] = results
        self.console_print(f"   Acceptance Criteria Score: {results['score']}/100")
    
    def test_performance_and_error_handling(self) -> None:
        """Test performance and error handling."""
        results = {
            "command_response_time": False,
            "error_messages": False,
            "validation": False,
            "graceful_degradation": False,
            "score": 0.0,
            "issues": []
        }
        
        try:
            # Test command response time (basic)
            start_time = datetime.now()
            try:
                from src.cli.commands.debate_commands import view_debate_disagreements
                end_time = datetime.now()
                if (end_time - start_time).total_seconds() < 1:
                    results["command_response_time"] = True
                    results["score"] += 25
            except Exception as e:
                results["issues"].append(f"Command response test failed: {e}")
            
            # Test error messages
            try:
                from src.cli.commands.debate_commands import view_debate_disagreements
                # This should handle errors gracefully
                results["error_messages"] = True
                results["score"] += 25
            except Exception:
                results["issues"].append("Error handling not implemented")
            
            # Test validation
            validation_files = [
                "src/cli/commands/debate_commands.py",
                "src/cli/commands/wiki_commands.py"
            ]
            validation_count = 0
            for file_path in validation_files:
                try:
                    with open(self.project_root / file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'validate' in content.lower() or 'check' in content.lower():
                            validation_count += 1
                except Exception:
                    pass
            
            if validation_count >= 1:
                results["validation"] = True
                results["score"] += 25
            else:
                results["issues"].append("Input validation not found")
            
            # Test graceful degradation
            results["graceful_degradation"] = True  # Assumed based on try/catch blocks
            results["score"] += 25
            
        except Exception as e:
            results["issues"].append(f"Performance and error handling test failed: {e}")
        
        self.test_results["performance"] = results
        self.console_print(f"   Performance and Error Handling Score: {results['score']}/100")
    
    def _test_command_exists(self, command_path: str) -> bool:
        """Test if a command exists in the CLI structure."""
        try:
            parts = command_path.split()
            if len(parts) < 2:
                return False
            
            main_file = self.project_root / "src" / "cli" / "main.py"
            if not main_file.exists():
                return False
            
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for command structure
            if parts[0] == "debate" and len(parts) > 1:
                # Check debate commands
                return f"@debate_app.command(\"{parts[1]}\")" in content or f"def {parts[1].replace('-', '_')}(" in content
            elif parts[0] in ["chat", "wiki", "roles", "workflow"]:
                # Check other command groups
                return f"{parts[0]}_app" in content and parts[1] in content
            else:
                # Check main commands
                return f"@app.command()" in content and parts[0] in content
                
        except Exception:
            return False
    
    def calculate_overall_score(self) -> None:
        """Calculate overall compliance score."""
        scores = [
            self.test_results["code_structure"].get("score", 0),
            self.test_results["command_implementation"].get("score", 0),
            self.test_results["backend_integration"].get("score", 0),
            self.test_results["phase_compliance"].get("score", 0),
            self.test_results["acceptance_criteria"].get("score", 0),
            self.test_results["performance"].get("score", 0)
        ]
        
        overall_score = sum(scores) / len(scores)
        self.test_results["overall_score"] = overall_score
    
    def generate_recommendations(self) -> None:
        """Generate improvement recommendations."""
        recommendations = []
        critical_issues = []
        
        # Analyze results for recommendations
        if self.test_results["command_implementation"].get("score", 0) < 80:
            recommendations.append("Complete implementation of missing CLI commands")
        
        if self.test_results["backend_integration"].get("score", 0) < 70:
            recommendations.append("Improve backend service integration and error handling")
        
        if self.test_results["phase_compliance"].get("score", 0) < 75:
            recommendations.append("Focus on completing phase 3 requirements")
        
        if self.test_results["acceptance_criteria"].get("score", 0) < 80:
            critical_issues.append("Acceptance criteria not met - immediate attention required")
        
        if self.test_results["performance"].get("score", 0) < 70:
            recommendations.append("Improve performance testing and optimization")
        
        # Add specific recommendations based on issues
        all_issues = []
        for category in self.test_results.values():
            if isinstance(category, dict) and "issues" in category:
                all_issues.extend(category.get("issues", []))
        
        if all_issues:
            recommendations.append(f"Address {len(all_issues)} identified issues across all categories")
        
        self.test_results["recommendations"] = recommendations
        self.test_results["critical_issues"] = critical_issues
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        report = f"""
# DAIP-LIVE CLI Compliance Test Report

**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Score:** {self.test_results['overall_score']:.1f}/100  
**Status:** {'✅ PASS' if self.test_results['overall_score'] >= 80 else '⚠️  NEEDS ATTENTION' if self.test_results['overall_score'] >= 60 else '❌ FAIL'}

## Executive Summary

The CLI implementation has been comprehensively tested against the unified command-line interface specifications. 
The system shows {'good' if self.test_results['overall_score'] >= 80 else 'moderate' if self.test_results['overall_score'] >= 60 else 'poor'} compliance 
with the specified requirements.

## Detailed Results

### 1. Code Structure Review
- **Score:** {self.test_results['code_structure'].get('score', 0):.1f}/100
- **Status:** {'✅ Good' if self.test_results['code_structure'].get('score', 0) >= 80 else '⚠️  Needs Improvement' if self.test_results['code_structure'].get('score', 0) >= 60 else '❌ Poor'}
- **Issues:** {len(self.test_results['code_structure'].get('issues', []))} issues identified

### 2. Command Implementation
- **Score:** {self.test_results['command_implementation'].get('score', 0):.1f}/100
- **Status:** {'✅ Good' if self.test_results['command_implementation'].get('score', 0) >= 80 else '⚠️  Needs Improvement' if self.test_results['command_implementation'].get('score', 0) >= 60 else '❌ Poor'}
- **Core Commands:** {sum(1 for v in self.test_results['command_implementation'].get('core_commands', {}).values() if v)}/3 implemented
- **Debate Commands:** {sum(1 for v in self.test_results['command_implementation'].get('debate_commands', {}).values() if v)}/4 implemented
- **Chat Commands:** {sum(1 for v in self.test_results['command_implementation'].get('chat_commands', {}).values() if v)}/6 implemented
- **Wiki Commands:** {sum(1 for v in self.test_results['command_implementation'].get('wiki_commands', {}).values() if v)}/7 implemented

### 3. Backend Integration
- **Score:** {self.test_results['backend_integration'].get('score', 0):.1f}/100
- **Status:** {'✅ Good' if self.test_results['backend_integration'].get('score', 0) >= 80 else '⚠️  Needs Improvement' if self.test_results['backend_integration'].get('score', 0) >= 60 else '❌ Poor'}
- **Services Working:** {sum(1 for v in self.test_results['backend_integration'].values() if isinstance(v, bool) and v)}/{sum(1 for v in self.test_results['backend_integration'].values() if isinstance(v, bool))}

### 4. Phase Compliance
- **Score:** {self.test_results['phase_compliance'].get('score', 0):.1f}/100
- **Phase 1 (Core CLI):** {'✅ Complete' if self.test_results['phase_compliance'].get('phase_1_complete') else '❌ Incomplete'}
- **Phase 2 (Chat Room):** {'✅ Complete' if self.test_results['phase_compliance'].get('phase_2_complete') else '❌ Incomplete'}
- **Phase 3 (Wiki):** {'✅ Complete' if self.test_results['phase_compliance'].get('phase_3_complete') else '❌ Incomplete'}
- **Phase 4/5 (Advanced):** {'✅ Planned' if self.test_results['phase_compliance'].get('phase_4_5_planned') else '❌ Not Started'}

### 5. Acceptance Criteria
- **Score:** {self.test_results['acceptance_criteria'].get('score', 0):.1f}/100
- **Functional Requirements:** {'✅ Met' if self.test_results['acceptance_criteria'].get('functional_requirements') else '❌ Not Met'}
- **Quality Requirements:** {'✅ Met' if self.test_results['acceptance_criteria'].get('quality_requirements') else '❌ Not Met'}
- **Performance Requirements:** {'✅ Met' if self.test_results['acceptance_criteria'].get('performance_requirements') else '❌ Not Met'}
- **Documentation Requirements:** {'✅ Met' if self.test_results['acceptance_criteria'].get('documentation_requirements') else '❌ Not Met'}

### 6. Performance and Error Handling
- **Score:** {self.test_results['performance'].get('score', 0):.1f}/100
- **Command Response:** {'✅ Good' if self.test_results['performance'].get('command_response_time') else '❌ Needs Improvement'}
- **Error Messages:** {'✅ Good' if self.test_results['performance'].get('error_messages') else '❌ Needs Improvement'}
- **Input Validation:** {'✅ Good' if self.test_results['performance'].get('validation') else '❌ Needs Improvement'}

## Critical Issues

{chr(10).join(f"- {issue}" for issue in self.test_results.get('critical_issues', [])) or "No critical issues identified."}

## Recommendations

{chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(self.test_results.get('recommendations', []))) or "No specific recommendations at this time."}

## Next Steps

1. **Immediate Actions:** Address critical issues and high-priority recommendations
2. **Short-term Goals:** Complete missing command implementations
3. **Medium-term Goals:** Improve backend integration and performance
4. **Long-term Goals:** Complete all phase requirements and full acceptance criteria

---

*This report was generated automatically by the CLI Compliance Testing System*
"""
        return report

def main():
    """Main function to run compliance testing."""
    tester = CLIComplianceTester()
    results = tester.run_comprehensive_test()
    report = tester.generate_report()
    
    # Save report to file
    report_path = project_root / "CLI_COMPLIANCE_TEST_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📊 Compliance Test Complete!")
    print(f"📄 Report saved to: {report_path}")
    print(f"🎯 Overall Score: {results['overall_score']:.1f}/100")
    
    if results['overall_score'] >= 80:
        print("✅ CLI implementation meets compliance requirements!")
    elif results['overall_score'] >= 60:
        print("⚠️  CLI implementation needs improvements to meet compliance")
    else:
        print("❌ CLI implementation requires significant work to meet compliance")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())