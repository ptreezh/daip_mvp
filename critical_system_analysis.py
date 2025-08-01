#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关键系统分析工具

基于第一性原理，从顶级测试工程师角度进行深度系统分析
专注于发现可能影响工程可用性的关键问题
"""

import asyncio
import sys
import time
import traceback
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import json

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class CriticalSystemAnalysis:
    """关键系统分析"""
    
    def __init__(self):
        self.critical_issues = []
        self.warnings = []
        self.performance_data = {}
    
    async def run_analysis(self):
        """运行关键系统分析"""
        print("🔍 启动关键系统分析")
        print("基于第一性原理，专注工程可用性")
        print("=" * 50)
        
        # 关键分析项目
        analyses = [
            ("核心架构完整性", self.analyze_core_architecture),
            ("实时对话能力", self.analyze_real_time_chat),
            ("LLM集成稳定性", self.analyze_llm_integration),
            ("用户体验关键路径", self.analyze_user_experience),
            ("并发处理能力", self.analyze_concurrency),
            ("错误恢复机制", self.analyze_error_recovery),
            ("性能瓶颈识别", self.analyze_performance_bottlenecks),
            ("数据一致性保证", self.analyze_data_consistency)
        ]
        
        for analysis_name, analysis_func in analyses:
            print(f"\n🔍 {analysis_name}")
            print("-" * 30)
            
            try:
                start_time = time.time()
                issues = await analysis_func()
                duration = time.time() - start_time
                
                if issues:
                    for issue in issues:
                        if issue['severity'] == 'CRITICAL':
                            self.critical_issues.append(issue)
                            print(f"🚨 严重: {issue['description']}")
                        else:
                            self.warnings.append(issue)
                            print(f"⚠️ 警告: {issue['description']}")
                else:
                    print("✅ 未发现关键问题")
                
                print(f"   分析耗时: {duration:.2f}秒")
                
            except Exception as e:
                critical_issue = {
                    'severity': 'CRITICAL',
                    'category': analysis_name,
                    'description': f"分析过程异常: {e}",
                    'impact': '无法完成系统分析',
                    'recommendation': '检查系统环境和依赖'
                }
                self.critical_issues.append(critical_issue)
                print(f"🚨 分析异常: {e}")
        
        await self.generate_final_report()
    
    async def analyze_core_architecture(self):
        """分析核心架构完整性"""
        issues = []
        
        try:
            # 检查关键模块导入
            critical_modules = {
                'MultiRoleDebateSystem': 'src.real_demo_system.multi_role_debate_system',
                'RealLLMIntegrator': 'src.real_demo_system.real_llm_integrator',
                'RoleManager': 'src.core_services.role_manager'
            }
            
            for class_name, module_path in critical_modules.items():
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    cls = getattr(module, class_name)
                    
                    # 验证关键方法存在
                    if class_name == 'MultiRoleDebateSystem':
                        required_methods = ['start_debate', 'get_debate_status']
                    elif class_name == 'RealLLMIntegrator':
                        required_methods = ['call_llm']
                    elif class_name == 'RoleManager':
                        required_methods = ['get_role']
                    
                    for method in required_methods:
                        if not hasattr(cls, method):
                            issues.append({
                                'severity': 'CRITICAL',
                                'description': f"{class_name}缺少关键方法{method}",
                                'impact': '核心功能无法使用',
                                'recommendation': f'实现{class_name}.{method}方法'
                            })
                
                except ImportError as e:
                    issues.append({
                        'severity': 'CRITICAL',
                        'description': f"无法导入{class_name}: {e}",
                        'impact': '系统无法启动',
                        'recommendation': '检查模块路径和依赖'
                    })
            
            # 测试基本实例化
            from src.core_services.role_manager import RoleManager
            role_manager = RoleManager()
            
            if len(role_manager._roles) == 0:
                issues.append({
                    'severity': 'CRITICAL',
                    'description': '角色管理器未加载任何角色',
                    'impact': '无法进行多角色对话',
                    'recommendation': '检查roles目录和角色文件'
                })
            elif len(role_manager._roles) < 10:
                issues.append({
                    'severity': 'WARNING',
                    'description': f'可用角色较少: {len(role_manager._roles)}个',
                    'impact': '用户选择受限',
                    'recommendation': '增加更多角色定义'
                })
            
        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'description': f'架构分析异常: {e}',
                'impact': '无法验证系统完整性',
                'recommendation': '检查系统环境'
            })
        
        return issues
    
    async def analyze_real_time_chat(self):
        """分析实时对话能力"""
        issues = []
        
        try:
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            from src.core_services.role_manager import RoleManager
            
            # 创建系统实例
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            
            # 测试辩论创建能力
            start_time = time.time()
            
            try:
                debate_result = await debate_system.start_debate(
                    debate_topic="测试实时对话能力",
                    participating_roles=["AI Ethics", "Business Ethics"],
                    time_limit_minutes=1
                )
                
                creation_time = time.time() - start_time
                
                if creation_time > 60:  # 1分钟
                    issues.append({
                        'severity': 'CRITICAL',
                        'description': f'辩论创建过慢: {creation_time:.1f}秒',
                        'impact': '用户等待时间过长',
                        'recommendation': '优化LLM调用和角色加载'
                    })
                elif creation_time > 30:  # 30秒
                    issues.append({
                        'severity': 'WARNING',
                        'description': f'辩论创建较慢: {creation_time:.1f}秒',
                        'impact': '用户体验受影响',
                        'recommendation': '考虑添加缓存机制'
                    })
                
                if not debate_result or 'debate_id' not in debate_result:
                    issues.append({
                        'severity': 'CRITICAL',
                        'description': '辩论创建失败',
                        'impact': '核心功能不可用',
                        'recommendation': '检查LLM连接和角色配置'
                    })
                else:
                    # 测试状态查询
                    debate_id = debate_result['debate_id']
                    status = debate_system.get_debate_status(debate_id)
                    
                    if not status:
                        issues.append({
                            'severity': 'WARNING',
                            'description': '无法获取辩论状态',
                            'impact': '用户无法监控进展',
                            'recommendation': '修复状态查询功能'
                        })
                
            except Exception as e:
                issues.append({
                    'severity': 'CRITICAL',
                    'description': f'辩论创建异常: {e}',
                    'impact': '实时对话功能不可用',
                    'recommendation': '检查LLM服务和网络连接'
                })
        
        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'description': f'实时对话分析异常: {e}',
                'impact': '无法验证对话能力',
                'recommendation': '检查系统组件'
            })
        
        return issues
    
    async def analyze_llm_integration(self):
        """分析LLM集成稳定性"""
        issues = []
        
        try:
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            
            llm_integrator = RealLLMIntegrator()
            
            # 测试基本LLM调用
            test_prompts = [
                "Hello, this is a test.",
                "请用中文回答这个问题。",
                "What is 2+2?",
            ]
            
            successful_calls = 0
            total_time = 0
            
            for prompt in test_prompts:
                try:
                    start_time = time.time()
                    record = await llm_integrator.call_llm(prompt, max_tokens=50)
                    call_time = time.time() - start_time
                    total_time += call_time
                    
                    if record.success and record.response.strip():
                        successful_calls += 1
                    else:
                        issues.append({
                            'severity': 'WARNING',
                            'description': f'LLM调用返回空响应',
                            'impact': 'AI角色可能无法正常回应',
                            'recommendation': '检查LLM配置和提示词'
                        })
                    
                    if call_time > 30:  # 30秒
                        issues.append({
                            'severity': 'WARNING',
                            'description': f'LLM响应过慢: {call_time:.1f}秒',
                            'impact': '实时对话体验差',
                            'recommendation': '优化LLM配置或更换模型'
                        })
                
                except Exception as e:
                    issues.append({
                        'severity': 'CRITICAL',
                        'description': f'LLM调用失败: {e}',
                        'impact': 'AI角色无法工作',
                        'recommendation': '检查Ollama服务状态'
                    })
            
            # 评估整体稳定性
            success_rate = successful_calls / len(test_prompts)
            avg_time = total_time / len(test_prompts) if len(test_prompts) > 0 else 0
            
            if success_rate < 0.8:  # 80%
                issues.append({
                    'severity': 'CRITICAL',
                    'description': f'LLM调用成功率过低: {success_rate:.1%}',
                    'impact': '系统不稳定',
                    'recommendation': '检查LLM服务配置'
                })
            
            self.performance_data['llm_success_rate'] = success_rate
            self.performance_data['llm_avg_response_time'] = avg_time
        
        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'description': f'LLM集成分析异常: {e}',
                'impact': '无法验证LLM功能',
                'recommendation': '检查LLM集成器配置'
            })
        
        return issues   
 
    async def analyze_user_experience(self):
        """分析用户体验关键路径"""
        issues = []
        
        try:
            # 模拟用户完整使用流程
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            from src.core_services.role_manager import RoleManager
            
            # 1. 系统启动时间
            start_time = time.time()
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            startup_time = time.time() - start_time
            
            if startup_time > 10:  # 10秒
                issues.append({
                    'severity': 'CRITICAL',
                    'description': f'系统启动过慢: {startup_time:.1f}秒',
                    'impact': '用户等待时间过长，可能放弃使用',
                    'recommendation': '优化组件初始化，添加进度提示'
                })
            
            # 2. 角色选择体验
            available_roles = list(role_manager._roles.keys())
            role_names = [role_manager._roles[rid].name for rid in available_roles[:10]]
            
            # 检查角色名称长度
            long_names = [name for name in role_names if len(name) > 80]
            if long_names:
                issues.append({
                    'severity': 'WARNING',
                    'description': f'{len(long_names)}个角色名称过长',
                    'impact': '界面显示困难，用户难以选择',
                    'recommendation': '简化角色名称或提供简短别名'
                })
            
            # 3. 错误消息友好性测试
            try:
                # 测试空输入
                result = await debate_system.start_debate(
                    debate_topic="",
                    participating_roles=[]
                )
                
                if isinstance(result, dict) and 'error' in result:
                    error_msg = result['error']
                    if any(tech_term in error_msg.lower() for tech_term in 
                          ['exception', 'traceback', 'null', 'none', 'error:']):
                        issues.append({
                            'severity': 'WARNING',
                            'description': '错误消息包含技术术语',
                            'impact': '用户难以理解错误原因',
                            'recommendation': '提供用户友好的错误提示'
                        })
            except Exception as e:
                error_msg = str(e)
                if len(error_msg) > 100 or 'Traceback' in error_msg:
                    issues.append({
                        'severity': 'WARNING',
                        'description': '异常消息对用户不友好',
                        'impact': '用户无法理解问题',
                        'recommendation': '捕获异常并提供友好提示'
                    })
            
            # 4. 响应时间用户感知
            self.performance_data['startup_time'] = startup_time
            self.performance_data['available_roles'] = len(available_roles)
        
        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'description': f'用户体验分析异常: {e}',
                'impact': '无法评估用户体验',
                'recommendation': '检查系统组件完整性'
            })
        
        return issues
    
    async def analyze_concurrency(self):
        """分析并发处理能力"""
        issues = []
        
        try:
            from src.core_services.role_manager import RoleManager
            
            # 测试并发角色查询
            role_manager = RoleManager()
            
            async def concurrent_role_query():
                try:
                    role = role_manager.get_role("AI Ethics")
                    return role is not None
                except Exception as e:
                    return str(e)
            
            # 创建并发任务
            tasks = [concurrent_role_query() for _ in range(20)]
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            concurrent_time = time.time() - start_time
            
            # 分析结果
            exceptions = [r for r in results if isinstance(r, (Exception, str)) and r != True and r != False]
            success_count = len([r for r in results if r is True])
            
            if exceptions:
                issues.append({
                    'severity': 'CRITICAL',
                    'description': f'并发操作异常: {len(exceptions)}个',
                    'impact': '多用户同时使用时可能出错',
                    'recommendation': '添加线程安全机制'
                })
            
            if concurrent_time > 5:  # 5秒
                issues.append({
                    'severity': 'WARNING',
                    'description': f'并发处理过慢: {concurrent_time:.1f}秒',
                    'impact': '高并发时性能下降',
                    'recommendation': '优化并发处理逻辑'
                })
            
            self.performance_data['concurrent_success_rate'] = success_count / len(tasks)
            self.performance_data['concurrent_time'] = concurrent_time
        
        except Exception as e:
            issues.append({
                'severity': 'WARNING',
                'description': f'并发分析异常: {e}',
                'impact': '无法评估并发能力',
                'recommendation': '检查异步处理实现'
            })
        
        return issues
    
    async def analyze_error_recovery(self):
        """分析错误恢复机制"""
        issues = []
        
        try:
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            from src.core_services.role_manager import RoleManager
            
            # 创建系统实例
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            
            # 测试各种错误场景的恢复能力
            error_scenarios = [
                ("不存在的角色", lambda: debate_system.start_debate("test", ["NonExistentRole"])),
                ("空话题", lambda: debate_system.start_debate("", ["AI Ethics"])),
                ("极长话题", lambda: debate_system.start_debate("A" * 10000, ["AI Ethics"])),
            ]
            
            recovery_failures = 0
            
            for scenario_name, test_func in error_scenarios:
                try:
                    result = await test_func()
                    
                    # 检查是否有合理的错误处理
                    if isinstance(result, dict) and 'error' in result:
                        # 这是期望的错误处理
                        continue
                    elif result is None:
                        # 也是合理的错误处理
                        continue
                    else:
                        # 如果没有错误处理，这可能是问题
                        issues.append({
                            'severity': 'WARNING',
                            'description': f'错误场景未被正确处理: {scenario_name}',
                            'impact': '异常情况下系统行为不可预测',
                            'recommendation': '添加输入验证和错误处理'
                        })
                
                except Exception as e:
                    # 检查异常是否被合理处理
                    if 'timeout' in str(e).lower() or 'invalid' in str(e).lower():
                        # 这是合理的异常
                        continue
                    else:
                        recovery_failures += 1
            
            if recovery_failures > 0:
                issues.append({
                    'severity': 'WARNING',
                    'description': f'{recovery_failures}个错误场景恢复失败',
                    'impact': '系统鲁棒性不足',
                    'recommendation': '完善异常处理和错误恢复机制'
                })
        
        except Exception as e:
            issues.append({
                'severity': 'WARNING',
                'description': f'错误恢复分析异常: {e}',
                'impact': '无法评估系统鲁棒性',
                'recommendation': '检查错误处理实现'
            })
        
        return issues
    
    async def analyze_performance_bottlenecks(self):
        """分析性能瓶颈"""
        issues = []
        
        try:
            # 系统资源使用分析
            process = psutil.Process()
            
            # 内存使用
            memory_mb = process.memory_info().rss / 1024 / 1024
            if memory_mb > 1000:  # 1GB
                issues.append({
                    'severity': 'WARNING',
                    'description': f'内存使用过高: {memory_mb:.1f}MB',
                    'impact': '可能影响系统性能',
                    'recommendation': '优化内存使用，添加内存监控'
                })
            
            # CPU使用
            cpu_percent = process.cpu_percent(interval=1)
            if cpu_percent > 80:  # 80%
                issues.append({
                    'severity': 'WARNING',
                    'description': f'CPU使用率高: {cpu_percent:.1f}%',
                    'impact': '系统响应可能变慢',
                    'recommendation': '优化计算密集型操作'
                })
            
            # 角色加载性能测试
            from src.core_services.role_manager import RoleManager
            
            start_time = time.time()
            role_manager = RoleManager()
            load_time = time.time() - start_time
            
            if load_time > 3:  # 3秒
                issues.append({
                    'severity': 'WARNING',
                    'description': f'角色加载过慢: {load_time:.1f}秒',
                    'impact': '系统启动时间长',
                    'recommendation': '优化角色加载，考虑懒加载'
                })
            
            # 角色查询性能
            start_time = time.time()
            for _ in range(100):
                role_manager.get_role("AI Ethics")
            query_time = time.time() - start_time
            
            if query_time > 0.5:  # 0.5秒
                issues.append({
                    'severity': 'WARNING',
                    'description': f'角色查询性能差: 100次查询{query_time:.2f}秒',
                    'impact': '频繁查询时响应慢',
                    'recommendation': '添加缓存机制'
                })
            
            self.performance_data.update({
                'memory_mb': memory_mb,
                'cpu_percent': cpu_percent,
                'role_load_time': load_time,
                'role_query_time': query_time
            })
        
        except Exception as e:
            issues.append({
                'severity': 'WARNING',
                'description': f'性能分析异常: {e}',
                'impact': '无法识别性能瓶颈',
                'recommendation': '检查性能监控实现'
            })
        
        return issues
    
    async def analyze_data_consistency(self):
        """分析数据一致性保证"""
        issues = []
        
        try:
            from src.core_services.role_manager import RoleManager
            
            role_manager = RoleManager()
            
            # 检查角色数据完整性
            if len(role_manager._roles) == 0:
                issues.append({
                    'severity': 'CRITICAL',
                    'description': '没有加载任何角色数据',
                    'impact': '系统无法正常工作',
                    'recommendation': '检查角色文件和加载逻辑'
                })
                return issues
            
            # 检查角色数据格式一致性
            sample_roles = list(role_manager._roles.items())[:10]
            format_issues = 0
            
            for role_id, role in sample_roles:
                # 检查必需属性
                if not hasattr(role, 'name') or not role.name:
                    format_issues += 1
                
                if not hasattr(role, 'description') or not role.description:
                    format_issues += 1
                
                # 检查ID一致性
                if hasattr(role, 'id') and role.id != role_id:
                    format_issues += 1
            
            if format_issues > 0:
                issues.append({
                    'severity': 'WARNING',
                    'description': f'{format_issues}个角色数据格式问题',
                    'impact': '可能导致角色功能异常',
                    'recommendation': '标准化角色数据格式'
                })
            
            # 检查角色名称唯一性
            role_names = [role.name for role in role_manager._roles.values()]
            duplicate_names = len(role_names) - len(set(role_names))
            
            if duplicate_names > 0:
                issues.append({
                    'severity': 'WARNING',
                    'description': f'{duplicate_names}个重复的角色名称',
                    'impact': '用户可能混淆不同角色',
                    'recommendation': '确保角色名称唯一性'
                })
            
            self.performance_data['total_roles'] = len(role_manager._roles)
            self.performance_data['format_issues'] = format_issues
        
        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'description': f'数据一致性分析异常: {e}',
                'impact': '无法验证数据完整性',
                'recommendation': '检查数据管理实现'
            })
        
        return issues   
 
    async def generate_final_report(self):
        """生成最终分析报告"""
        print("\n" + "=" * 50)
        print("🎯 关键系统分析报告")
        print("=" * 50)
        
        critical_count = len(self.critical_issues)
        warning_count = len(self.warnings)
        total_issues = critical_count + warning_count
        
        print(f"严重问题: {critical_count} 个 🚨")
        print(f"警告问题: {warning_count} 个 ⚠️")
        print(f"总计问题: {total_issues} 个")
        
        # 严重问题详情
        if self.critical_issues:
            print(f"\n🚨 严重问题 (必须修复):")
            print("-" * 30)
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"{i}. {issue['description']}")
                print(f"   影响: {issue['impact']}")
                print(f"   建议: {issue['recommendation']}")
                print()
        
        # 关键警告
        if self.warnings:
            print(f"\n⚠️ 重要警告 (建议修复):")
            print("-" * 30)
            for i, warning in enumerate(self.warnings[:5], 1):  # 只显示前5个
                print(f"{i}. {warning['description']}")
                print(f"   建议: {warning['recommendation']}")
            
            if len(self.warnings) > 5:
                print(f"   ... 还有 {len(self.warnings) - 5} 个警告")
        
        # 性能指标摘要
        if self.performance_data:
            print(f"\n📊 关键性能指标:")
            print("-" * 30)
            
            if 'startup_time' in self.performance_data:
                print(f"系统启动时间: {self.performance_data['startup_time']:.1f}秒")
            
            if 'llm_success_rate' in self.performance_data:
                print(f"LLM调用成功率: {self.performance_data['llm_success_rate']:.1%}")
            
            if 'llm_avg_response_time' in self.performance_data:
                print(f"LLM平均响应时间: {self.performance_data['llm_avg_response_time']:.1f}秒")
            
            if 'memory_mb' in self.performance_data:
                print(f"内存使用: {self.performance_data['memory_mb']:.1f}MB")
            
            if 'total_roles' in self.performance_data:
                print(f"可用角色数量: {self.performance_data['total_roles']}个")
        
        # 工程可用性评估
        print(f"\n🎯 工程可用性评估:")
        print("-" * 30)
        
        if critical_count == 0:
            if warning_count <= 3:
                assessment = "优秀"
                recommendation = "✅ 系统已准备好投入生产使用"
                color = "🟢"
            elif warning_count <= 8:
                assessment = "良好"
                recommendation = "⚠️ 系统基本可用，建议修复警告问题"
                color = "🟡"
            else:
                assessment = "一般"
                recommendation = "🔧 系统可用但需要优化"
                color = "🟠"
        else:
            assessment = "需要修复"
            recommendation = "🚨 必须修复严重问题后才能使用"
            color = "🔴"
        
        print(f"{color} 评估结果: {assessment}")
        print(f"建议: {recommendation}")
        
        # 关键发现总结
        print(f"\n💡 关键发现:")
        print("-" * 30)
        
        key_findings = []
        
        # 基于分析结果生成关键发现
        if any('LLM' in issue['description'] for issue in self.critical_issues):
            key_findings.append("LLM集成存在严重问题，影响AI对话功能")
        
        if any('启动' in issue['description'] for issue in self.critical_issues + self.warnings):
            key_findings.append("系统启动性能需要优化")
        
        if any('角色' in issue['description'] for issue in self.critical_issues + self.warnings):
            key_findings.append("角色管理系统需要改进")
        
        if any('并发' in issue['description'] for issue in self.warnings):
            key_findings.append("并发处理能力有待提升")
        
        if not key_findings:
            key_findings.append("系统整体架构稳定，主要是细节优化问题")
        
        for finding in key_findings:
            print(f"• {finding}")
        
        # 下一步行动建议
        print(f"\n🚀 下一步行动建议:")
        print("-" * 30)
        
        if critical_count > 0:
            print("1. 立即修复所有严重问题")
            print("2. 重新运行系统分析验证修复效果")
            print("3. 修复完成后再考虑警告问题")
        else:
            print("1. 优先修复影响用户体验的警告问题")
            print("2. 持续监控系统性能指标")
            print("3. 建立定期系统健康检查机制")
        
        # 保存详细报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'assessment': assessment,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'performance_data': self.performance_data,
            'key_findings': key_findings,
            'total_issues': total_issues
        }
        
        report_file = Path("critical_system_analysis_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        return critical_count == 0 and warning_count <= 8


async def main():
    """主函数"""
    print("🔍 关键系统分析工具")
    print("基于第一性原理，专注工程可用性")
    print("从顶级测试工程师角度进行深度分析")
    print()
    
    analysis = CriticalSystemAnalysis()
    
    try:
        await analysis.run_analysis()
        return True
    except Exception as e:
        print(f"❌ 分析异常: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 分析被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 分析异常: {e}")
        sys.exit(1)