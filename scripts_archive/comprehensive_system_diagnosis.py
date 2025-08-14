#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面系统诊断工具

从顶级测试工程师的角度，进行深度系统分析和问题检测
基于第一性原理，检测所有可能的系统问题
"""

import asyncio
import sys
import time
import traceback
import psutil
import gc
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ComprehensiveSystemDiagnosis:
    """全面系统诊断"""
    
    def __init__(self):
        self.diagnosis_results = []
        self.critical_issues = []
        self.warnings = []
        self.performance_metrics = {}
        
    async def run_full_diagnosis(self):
        """运行全面诊断"""
        print("🔍 启动全面系统诊断")
        print("基于第一性原理和顶级测试工程师标准")
        print("=" * 60)
        
        # 诊断类别
        diagnosis_categories = [
            ("架构完整性检查", self.check_architecture_integrity),
            ("依赖关系验证", self.check_dependency_integrity),
            ("内存泄漏检测", self.check_memory_leaks),
            ("并发安全性检查", self.check_concurrency_safety),
            ("错误处理完整性", self.check_error_handling),
            ("性能瓶颈分析", self.check_performance_bottlenecks),
            ("数据一致性验证", self.check_data_consistency),
            ("用户体验问题检测", self.check_user_experience_issues),
            ("安全漏洞扫描", self.check_security_vulnerabilities),
            ("边界条件测试", self.check_edge_cases)
        ]
        
        for category_name, check_func in diagnosis_categories:
            print(f"\n🔍 {category_name}")
            print("-" * 40)
            
            try:
                start_time = time.time()
                issues = await check_func()
                duration = time.time() - start_time
                
                if issues:
                    for issue in issues:
                        if issue['severity'] == 'CRITICAL':
                            self.critical_issues.append(issue)
                            print(f"🚨 严重: {issue['description']}")
                        elif issue['severity'] == 'WARNING':
                            self.warnings.append(issue)
                            print(f"⚠️ 警告: {issue['description']}")
                        else:
                            print(f"ℹ️ 信息: {issue['description']}")
                else:
                    print("✅ 未发现问题")
                
                self.diagnosis_results.append({
                    'category': category_name,
                    'duration': duration,
                    'issues_found': len(issues),
                    'issues': issues
                })
                
            except Exception as e:
                error_issue = {
                    'severity': 'CRITICAL',
                    'description': f"诊断过程异常: {e}",
                    'details': traceback.format_exc()
                }
                self.critical_issues.append(error_issue)
                print(f"🚨 诊断异常: {e}")
        
        await self.generate_diagnosis_report()
    
    async def check_architecture_integrity(self):
        """检查架构完整性"""
        issues = []
        
        try:
            # 检查核心模块导入
            core_modules = [
                'src.real_demo_system.multi_role_debate_system',
                'src.real_demo_system.real_llm_integrator',
                'src.core_services.role_manager',
                'src.debate_system.debate_state_manager'
            ]
            
            for module_name in core_modules:
                try:
                    __import__(module_name)
                except ImportError as e:
                    issues.append({
                        'severity': 'CRITICAL',
                        'description': f"核心模块导入失败: {module_name}",
                        'details': str(e)
                    })
            
            # 检查类接口完整性
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            from src.core_services.role_manager import RoleManager
            
            # 验证关键方法存在
            required_methods = {
                'MultiRoleDebateSystem': ['start_debate', 'get_debate_status'],
                'RealLLMIntegrator': ['call_llm'],
                'RoleManager': ['get_role', 'get_role_by_id']
            }
            
            for class_name, methods in required_methods.items():
                cls = locals()[class_name]
                for method in methods:
                    if not hasattr(cls, method):
                        issues.append({
                            'severity': 'CRITICAL',
                            'description': f"{class_name}缺少必需方法: {method}",
                            'details': f"类{class_name}应该实现{method}方法"
                        })
            
        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'description': "架构完整性检查异常",
                'details': str(e)
            })
        
        return issues    
  
  async def check_dependency_integrity(self):
        """检查依赖关系完整性"""
        issues = []
        
        try:
            # 检查Python版本兼容性
            if sys.version_info < (3, 8):
                issues.append({
                    'severity': 'CRITICAL',
                    'description': f"Python版本过低: {sys.version}",
                    'details': "需要Python 3.8或更高版本"
                })
            
            # 检查关键依赖包
            required_packages = [
                'asyncio', 'json', 'pathlib', 'datetime', 'typing',
                'dataclasses', 'enum', 'uuid', 'logging'
            ]
            
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    issues.append({
                        'severity': 'CRITICAL',
                        'description': f"缺少必需包: {package}",
                        'details': f"请安装{package}包"
                    })
            
            # 检查可选依赖包
            optional_packages = ['httpx', 'ollama', 'openai', 'anthropic']
            missing_optional = []
            
            for package in optional_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_optional.append(package)
            
            if missing_optional:
                issues.append({
                    'severity': 'WARNING',
                    'description': f"缺少可选包: {missing_optional}",
                    'details': "可能影响LLM集成功能"
                })
            
        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'description': "依赖检查异常",
                'details': str(e)
            })
        
        return issues
    
    async def check_memory_leaks(self):
        """检查内存泄漏"""
        issues = []
        
        try:
            # 记录初始内存使用
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 创建和销毁多个对象实例
            objects = []
            for i in range(100):
                try:
                    from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
                    from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
                    from src.core_services.role_manager import RoleManager
                    
                    # 创建对象但不初始化LLM连接
                    role_manager = RoleManager()
                    objects.append(role_manager)
                    
                except Exception as e:
                    issues.append({
                        'severity': 'WARNING',
                        'description': f"对象创建失败: {e}",
                        'details': f"在第{i}次创建时失败"
                    })
                    break
            
            # 检查内存增长
            peak_memory = process.memory_info().rss / 1024 / 1024
            memory_growth = peak_memory - initial_memory
            
            # 清理对象
            objects.clear()
            gc.collect()
            await asyncio.sleep(1)
            
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_after_cleanup = final_memory - initial_memory
            
            # 分析内存泄漏
            if memory_after_cleanup > memory_growth * 0.5:
                issues.append({
                    'severity': 'WARNING',
                    'description': f"可能存在内存泄漏",
                    'details': f"清理后仍有{memory_after_cleanup:.2f}MB内存未释放"
                })
            
            if memory_growth > 100:  # 100MB
                issues.append({
                    'severity': 'WARNING',
                    'description': f"内存使用过高",
                    'details': f"创建100个对象消耗{memory_growth:.2f}MB内存"
                })
            
        except Exception as e:
            issues.append({
                'severity': 'WARNING',
                'description': "内存泄漏检查异常",
                'details': str(e)
            })
        
        return issues
    
    async def check_concurrency_safety(self):
        """检查并发安全性"""
        issues = []
        
        try:
            # 测试异步操作的并发安全性
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            from src.core_services.role_manager import RoleManager
            
            # 创建多个并发任务
            async def concurrent_operation():
                try:
                    role_manager = RoleManager()
                    # 模拟并发访问
                    role = role_manager.get_role("AI Ethics")
                    return role is not None
                except Exception as e:
                    return str(e)
            
            # 运行并发测试
            tasks = [concurrent_operation() for _ in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 分析结果
            exceptions = [r for r in results if isinstance(r, Exception)]
            if exceptions:
                issues.append({
                    'severity': 'WARNING',
                    'description': f"并发操作异常: {len(exceptions)}个",
                    'details': f"异常类型: {[type(e).__name__ for e in exceptions[:3]]}"
                })
            
            # 检查线程安全
            import threading
            thread_results = []
            
            def thread_operation():
                try:
                    role_manager = RoleManager()
                    role = role_manager.get_role("Business Ethics")
                    thread_results.append(role is not None)
                except Exception as e:
                    thread_results.append(str(e))
            
            threads = [threading.Thread(target=thread_operation) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            thread_exceptions = [r for r in thread_results if isinstance(r, str)]
            if thread_exceptions:
                issues.append({
                    'severity': 'WARNING',
                    'description': f"线程安全问题: {len(thread_exceptions)}个",
                    'details': f"线程异常: {thread_exceptions[:2]}"
                })
            
        except Exception as e:
            issues.append({
                'severity': 'WARNING',
                'description': "并发安全检查异常",
                'details': str(e)
            })
        
        return issues    

    async def check_error_handling(self):
        """检查错误处理完整性"""
        issues = []
        
        try:
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            from src.core_services.role_manager import RoleManager
            
            # 测试各种错误情况
            error_scenarios = [
                ("空角色ID", lambda rm: rm.get_role("")),
                ("不存在的角色", lambda rm: rm.get_role("NonExistentRole")),
                ("None参数", lambda rm: rm.get_role(None)),
            ]
            
            role_manager = RoleManager()
            
            for scenario_name, test_func in error_scenarios:
                try:
                    result = test_func(role_manager)
                    if result is not None and not isinstance(result, (bool, type(None))):
                        issues.append({
                            'severity': 'WARNING',
                            'description': f"错误处理不当: {scenario_name}",
                            'details': f"应该返回None或抛出异常，但返回了{type(result)}"
                        })
                except Exception as e:
                    # 这是期望的行为，说明错误处理正常
                    pass
            
            # 测试LLM集成的错误处理
            try:
                llm_integrator = RealLLMIntegrator()
                
                # 测试空提示
                try:
                    record = await llm_integrator.call_llm("")
                    if not hasattr(record, 'success'):
                        issues.append({
                            'severity': 'WARNING',
                            'description': "LLM调用返回格式不正确",
                            'details': "返回对象缺少success属性"
                        })
                except Exception:
                    # 期望的错误处理
                    pass
                
            except Exception as e:
                issues.append({
                    'severity': 'WARNING',
                    'description': "LLM集成器初始化问题",
                    'details': str(e)
                })
            
        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'description': "错误处理检查异常",
                'details': str(e)
            })
        
        return issues
    
    async def check_performance_bottlenecks(self):
        """检查性能瓶颈"""
        issues = []
        
        try:
            # 测试组件初始化时间
            start_time = time.time()
            
            from src.core_services.role_manager import RoleManager
            role_manager = RoleManager()
            
            init_time = time.time() - start_time
            
            if init_time > 5.0:  # 5秒
                issues.append({
                    'severity': 'WARNING',
                    'description': f"RoleManager初始化过慢: {init_time:.2f}秒",
                    'details': "建议优化角色加载逻辑"
                })
            
            # 测试角色查询性能
            start_time = time.time()
            for i in range(100):
                role_manager.get_role("AI Ethics")
            query_time = time.time() - start_time
            
            if query_time > 1.0:  # 1秒
                issues.append({
                    'severity': 'WARNING',
                    'description': f"角色查询性能差: 100次查询耗时{query_time:.2f}秒",
                    'details': "建议添加缓存机制"
                })
            
            # 检查内存使用效率
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            if memory_usage > 500:  # 500MB
                issues.append({
                    'severity': 'WARNING',
                    'description': f"内存使用过高: {memory_usage:.2f}MB",
                    'details': "建议优化内存使用"
                })
            
            # 检查CPU使用
            cpu_percent = process.cpu_percent(interval=1)
            if cpu_percent > 50:  # 50%
                issues.append({
                    'severity': 'WARNING',
                    'description': f"CPU使用率高: {cpu_percent:.1f}%",
                    'details': "可能存在性能瓶颈"
                })
            
        except Exception as e:
            issues.append({
                'severity': 'WARNING',
                'description': "性能检查异常",
                'details': str(e)
            })
        
        return issues
    
    async def check_data_consistency(self):
        """检查数据一致性"""
        issues = []
        
        try:
            from src.core_services.role_manager import RoleManager
            
            role_manager = RoleManager()
            
            # 检查角色数据一致性
            total_roles = len(role_manager._roles)
            if total_roles == 0:
                issues.append({
                    'severity': 'CRITICAL',
                    'description': "没有加载任何角色",
                    'details': "角色管理器为空"
                })
            
            # 检查角色数据格式
            sample_roles = list(role_manager._roles.items())[:5]
            for role_id, role in sample_roles:
                if not hasattr(role, 'name'):
                    issues.append({
                        'severity': 'CRITICAL',
                        'description': f"角色{role_id}缺少name属性",
                        'details': "角色对象格式不正确"
                    })
                
                if not hasattr(role, 'description'):
                    issues.append({
                        'severity': 'WARNING',
                        'description': f"角色{role_id}缺少description属性",
                        'details': "可能影响角色理解"
                    })
            
            # 检查角色ID一致性
            for role_id, role in sample_roles:
                if hasattr(role, 'id') and role.id != role_id:
                    issues.append({
                        'severity': 'WARNING',
                        'description': f"角色ID不一致: {role_id} vs {role.id}",
                        'details': "可能导致查询问题"
                    })
            
        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'description': "数据一致性检查异常",
                'details': str(e)
            })
        
        return issues    
   
 async def check_user_experience_issues(self):
        """检查用户体验问题"""
        issues = []
        
        try:
            # 检查用户界面响应性
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            from src.core_services.role_manager import RoleManager
            
            # 模拟用户操作流程
            start_time = time.time()
            
            # 1. 系统初始化时间
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            
            init_time = time.time() - start_time
            
            if init_time > 10.0:  # 10秒
                issues.append({
                    'severity': 'CRITICAL',
                    'description': f"系统初始化过慢: {init_time:.2f}秒",
                    'details': "用户等待时间过长，影响体验"
                })
            elif init_time > 5.0:  # 5秒
                issues.append({
                    'severity': 'WARNING',
                    'description': f"系统初始化较慢: {init_time:.2f}秒",
                    'details': "建议优化启动速度"
                })
            
            # 2. 角色选择体验
            available_roles = list(role_manager._roles.keys())[:10]
            if len(available_roles) < 5:
                issues.append({
                    'severity': 'WARNING',
                    'description': f"可选角色过少: {len(available_roles)}个",
                    'details': "可能限制用户选择"
                })
            
            # 3. 角色名称可读性
            long_names = [name for name in [role_manager._roles[rid].name for rid in available_roles] 
                         if len(name) > 100]
            if long_names:
                issues.append({
                    'severity': 'WARNING',
                    'description': f"角色名称过长: {len(long_names)}个",
                    'details': "可能影响界面显示"
                })
            
            # 4. 错误消息友好性
            try:
                # 测试错误消息
                debate_result = await debate_system.start_debate(
                    debate_topic="",  # 空话题
                    participating_roles=[],  # 空角色列表
                )
                
                if isinstance(debate_result, dict) and 'error' in debate_result:
                    error_msg = debate_result['error']
                    if len(error_msg) > 200 or 'Exception' in error_msg:
                        issues.append({
                            'severity': 'WARNING',
                            'description': "错误消息不够用户友好",
                            'details': f"错误消息: {error_msg[:100]}..."
                        })
                
            except Exception as e:
                # 检查异常消息是否用户友好
                error_msg = str(e)
                if 'Traceback' in error_msg or len(error_msg) > 200:
                    issues.append({
                        'severity': 'WARNING',
                        'description': "异常消息不够用户友好",
                        'details': f"异常: {error_msg[:100]}..."
                    })
            
        except Exception as e:
            issues.append({
                'severity': 'WARNING',
                'description': "用户体验检查异常",
                'details': str(e)
            })
        
        return issues
    
    async def check_security_vulnerabilities(self):
        """检查安全漏洞"""
        issues = []
        
        try:
            # 检查输入验证
            from src.core_services.role_manager import RoleManager
            
            role_manager = RoleManager()
            
            # 测试恶意输入
            malicious_inputs = [
                "../../../etc/passwd",  # 路径遍历
                "<script>alert('xss')</script>",  # XSS
                "'; DROP TABLE users; --",  # SQL注入
                "{{7*7}}",  # 模板注入
                "\x00\x01\x02",  # 二进制数据
            ]
            
            for malicious_input in malicious_inputs:
                try:
                    result = role_manager.get_role(malicious_input)
                    # 如果没有抛出异常，检查是否有不当处理
                    if result is not None:
                        issues.append({
                            'severity': 'WARNING',
                            'description': f"可能的输入验证问题",
                            'details': f"恶意输入'{malicious_input[:20]}...'未被正确处理"
                        })
                except Exception:
                    # 抛出异常是期望的行为
                    pass
            
            # 检查文件访问安全
            try:
                # 测试是否能访问系统文件
                test_paths = ["../../../etc/passwd", "C:\\Windows\\System32\\config\\SAM"]
                for test_path in test_paths:
                    if Path(test_path).exists():
                        issues.append({
                            'severity': 'CRITICAL',
                            'description': f"可能的路径遍历漏洞",
                            'details': f"能够访问系统文件: {test_path}"
                        })
            except Exception:
                pass
            
            # 检查敏感信息泄露
            import os
            sensitive_vars = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']
            for var in sensitive_vars:
                if var in os.environ:
                    issues.append({
                        'severity': 'WARNING',
                        'description': f"环境变量可能包含敏感信息: {var}",
                        'details': "建议检查敏感信息处理"
                    })
            
        except Exception as e:
            issues.append({
                'severity': 'WARNING',
                'description': "安全检查异常",
                'details': str(e)
            })
        
        return issues
    
    async def check_edge_cases(self):
        """检查边界条件"""
        issues = []
        
        try:
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            from src.core_services.role_manager import RoleManager
            
            # 创建系统实例
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            
            # 边界条件测试
            edge_cases = [
                # 极长输入
                ("极长话题", "A" * 10000),
                # 特殊字符
                ("特殊字符话题", "话题包含特殊字符: !@#$%^&*()_+{}|:<>?[]\\;'\",./ 和 emoji 😀🎉🔥"),
                # 多语言
                ("多语言话题", "English中文日本語한국어العربيةРусский"),
                # 空白字符
                ("空白字符话题", "   \t\n\r   "),
            ]
            
            for case_name, test_input in edge_cases:
                try:
                    # 测试辩论创建
                    result = await debate_system.start_debate(
                        debate_topic=test_input,
                        participating_roles=["AI Ethics"],
                        time_limit_minutes=1
                    )
                    
                    if isinstance(result, dict) and 'error' in result:
                        # 检查错误处理是否合适
                        error_msg = result['error']
                        if 'Exception' in error_msg or 'Traceback' in error_msg:
                            issues.append({
                                'severity': 'WARNING',
                                'description': f"边界条件错误处理不当: {case_name}",
                                'details': f"错误消息包含技术细节: {error_msg[:100]}..."
                            })
                    
                except Exception as e:
                    # 检查异常是否合理
                    if 'timeout' not in str(e).lower() and 'limit' not in str(e).lower():
                        issues.append({
                            'severity': 'WARNING',
                            'description': f"边界条件异常: {case_name}",
                            'details': f"异常: {str(e)[:100]}..."
                        })
            
            # 测试资源限制
            try:
                # 测试大量角色
                many_roles = list(role_manager._roles.keys())[:50]  # 50个角色
                result = await debate_system.start_debate(
                    debate_topic="测试大量角色",
                    participating_roles=many_roles,
                    time_limit_minutes=1
                )
                
                if isinstance(result, dict) and 'error' not in result:
                    issues.append({
                        'severity': 'WARNING',
                        'description': "缺少角色数量限制",
                        'details': "系统允许过多角色参与，可能影响性能"
                    })
                
            except Exception as e:
                # 这可能是期望的行为
                pass
            
        except Exception as e:
            issues.append({
                'severity': 'WARNING',
                'description': "边界条件检查异常",
                'details': str(e)
            })
        
        return issues    

    async def generate_diagnosis_report(self):
        """生成诊断报告"""
        print("\n" + "=" * 60)
        print("🎯 全面系统诊断报告")
        print("=" * 60)
        
        total_categories = len(self.diagnosis_results)
        total_issues = sum(len(result['issues']) for result in self.diagnosis_results)
        critical_count = len(self.critical_issues)
        warning_count = len(self.warnings)
        
        print(f"诊断类别: {total_categories}")
        print(f"发现问题: {total_issues} 个")
        print(f"严重问题: {critical_count} 个 🚨")
        print(f"警告问题: {warning_count} 个 ⚠️")
        
        # 严重问题详情
        if self.critical_issues:
            print(f"\n🚨 严重问题详情:")
            print("-" * 40)
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"{i}. {issue['description']}")
                print(f"   详情: {issue['details']}")
                print()
        
        # 警告问题摘要
        if self.warnings:
            print(f"\n⚠️ 警告问题摘要:")
            print("-" * 40)
            warning_categories = {}
            for warning in self.warnings:
                category = warning['description'].split(':')[0]
                warning_categories[category] = warning_categories.get(category, 0) + 1
            
            for category, count in warning_categories.items():
                print(f"• {category}: {count} 个")
        
        # 性能指标
        print(f"\n📊 性能指标:")
        print("-" * 40)
        process = psutil.Process()
        print(f"内存使用: {process.memory_info().rss / 1024 / 1024:.2f} MB")
        print(f"CPU使用: {process.cpu_percent():.1f}%")
        
        # 总体评估
        print(f"\n🎯 总体评估:")
        print("-" * 40)
        
        if critical_count == 0 and warning_count <= 5:
            print("✅ 系统状态良好，可以投入生产使用")
            overall_status = "GOOD"
        elif critical_count == 0 and warning_count <= 15:
            print("⚠️ 系统基本可用，建议修复警告问题")
            overall_status = "ACCEPTABLE"
        elif critical_count <= 2:
            print("🚨 系统存在问题，需要修复严重问题后使用")
            overall_status = "NEEDS_FIXING"
        else:
            print("❌ 系统存在严重问题，不建议使用")
            overall_status = "CRITICAL"
        
        # 保存诊断报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'summary': {
                'total_categories': total_categories,
                'total_issues': total_issues,
                'critical_issues': critical_count,
                'warning_issues': warning_count
            },
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'detailed_results': self.diagnosis_results,
            'performance_metrics': {
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent()
            }
        }
        
        report_file = Path("comprehensive_diagnosis_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        return overall_status == "GOOD" or overall_status == "ACCEPTABLE"


async def main():
    """主函数"""
    print("🔍 全面系统诊断工具")
    print("基于第一性原理和顶级测试工程师标准")
    print("检测所有可能的系统问题")
    print()
    
    diagnosis = ComprehensiveSystemDiagnosis()
    
    try:
        await diagnosis.run_full_diagnosis()
        return True
    except Exception as e:
        print(f"❌ 诊断异常: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 诊断被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 诊断异常: {e}")
        sys.exit(1)