#!/usr/bin/env python3
"""
TUI命令实现状态分析器

分析TUI中所有命令的实现状态，识别未实现的命令并从帮助文档中移除
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
import importlib.util

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


@dataclass
class CommandInfo:
    """命令信息"""
    name: str
    description: str
    implemented: bool
    handler_method: Optional[str] = None
    issues: List[str] = None


class TUICommandAnalyzer:
    """TUI命令分析器"""
    
    def __init__(self):
        self.tui_file = Path("src/daip_live/tui.py")
        self.implemented_commands: Dict[str, CommandInfo] = {}
        self.help_commands: Dict[str, str] = {}
        self.unimplemented_commands: List[str] = []
        
    def analyze_tui_commands(self) -> Dict[str, CommandInfo]:
        """分析TUI文件中的命令实现"""
        print("🔍 分析TUI命令实现状态...")
        
        try:
            with open(self.tui_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找所有命令处理方法
            command_pattern = r'def _handle_(\w+)_command\s*\('
            matches = re.findall(command_pattern, content)
            
            for command_name in matches:
                # 检查方法实现
                method_pattern = rf'def _handle_{command_name}_command\s*\([^)]*\):(.*?)(?=\n    def|\nclass|\Z)'
                method_match = re.search(method_pattern, content, re.DOTALL)
                
                if method_match:
                    method_body = method_match.group(1)
                    
                    # 检查是否只是占位符实现
                    is_placeholder = self._is_placeholder_implementation(method_body)
                    
                    # 检查是否有错误或未完成的功能
                    issues = self._analyze_implementation_issues(method_body)
                    
                    self.implemented_commands[command_name] = CommandInfo(
                        name=command_name,
                        description=f"Handle {command_name} command",
                        implemented=not is_placeholder,
                        handler_method=f"_handle_{command_name}_command",
                        issues=issues
                    )
                    
                    if is_placeholder:
                        self.unimplemented_commands.append(command_name)
                        print(f"  ❌ 命令 '{command_name}' 未完全实现")
                    else:
                        print(f"  ✅ 命令 '{command_name}' 已实现")
            
            # 查找帮助文本中的命令
            self._extract_help_commands(content)
            
            return self.implemented_commands
            
        except Exception as e:
            print(f"❌ 分析TUI命令时出错: {e}")
            return {}
    
    def _is_placeholder_implementation(self, method_body: str) -> bool:
        """检查是否是占位符实现"""
        placeholder_patterns = [
            r'pass\s*$',
            r'raise NotImplementedError',
            r'# TODO.*implement',
            r'# FIXME.*implement',
            r'print.*not.*implement',
            r'self\._update_log_view.*not.*implement',
            r'self\._update_log_view.*TODO',
            r'self\._update_log_view.*coming soon',
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, method_body, re.IGNORECASE):
                return True
        
        # 检查方法体是否太简单（少于3行有效代码）
        lines = [line.strip() for line in method_body.split('\n') if line.strip() and not line.strip().startswith('#')]
        if len(lines) < 3:
            return True
            
        return False
    
    def _analyze_implementation_issues(self, method_body: str) -> List[str]:
        """分析实现中的问题"""
        issues = []
        
        # 检查硬编码的错误消息
        if re.search(r'self\._update_log_view.*"未实现"', method_body):
            issues.append("包含硬编码的未实现消息")
        
        # 检查异常处理
        if 'except Exception' in method_body and 'pass' in method_body:
            issues.append("异常处理不完整")
        
        # 检查返回值
        if 'return' not in method_body and 'yield' not in method_body:
            issues.append("缺少返回值")
        
        return issues
    
    def _extract_help_commands(self, content: str) -> None:
        """提取帮助文本中的命令"""
        # 查找帮助文本
        help_pattern = r'HELP_TEXT\s*=\s*"""(.*?)"""'
        help_match = re.search(help_pattern, content, re.DOTALL)
        
        if help_match:
            help_text = help_match.group(1)
            
            # 提取命令名称
            command_pattern = r'/(\w+)(?:\s+-\s+(.+))?'
            matches = re.findall(command_pattern, help_text)
            
            for command_name, description in matches:
                self.help_commands[command_name] = description.strip() if description else ""
    
    def generate_clean_help_text(self) -> str:
        """生成清理后的帮助文本"""
        print("\n📝 生成清理后的帮助文本...")
        
        # 只保留已实现的命令
        implemented_help_commands = []
        
        for command_name, description in self.help_commands.items():
            if command_name in self.implemented_commands and self.implemented_commands[command_name].implemented:
                if description:
                    implemented_help_commands.append(f"/{command_name} - {description}")
                else:
                    implemented_help_commands.append(f"/{command_name}")
        
        # 按字母顺序排序
        implemented_help_commands.sort()
        
        # 生成帮助文本
        help_text = """可用命令：
"""
        
        for command in implemented_help_commands:
            help_text += f"• {command}\n"
        
        help_text += """
使用 /help <命令名> 获取特定命令的详细帮助。
"""
        
        return help_text
    
    def update_help_text(self) -> bool:
        """更新TUI文件中的帮助文本"""
        try:
            with open(self.tui_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 生成新的帮助文本
            new_help_text = self.generate_clean_help_text()
            
            # 替换帮助文本
            help_pattern = r'HELP_TEXT\s*=\s*"""(.*?)"""'
            new_content = re.sub(help_pattern, f'HELP_TEXT = """{new_help_text}"""', content, flags=re.DOTALL)
            
            # 写回文件
            with open(self.tui_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已更新帮助文本，移除了 {len(self.unimplemented_commands)} 个未实现的命令")
            return True
            
        except Exception as e:
            print(f"❌ 更新帮助文本时出错: {e}")
            return False
    
    def generate_report(self) -> str:
        """生成分析报告"""
        report = []
        report.append("# TUI命令实现状态分析报告")
        report.append(f"分析时间: {self._get_current_time()}")
        report.append("")
        
        # 统计信息
        total_commands = len(self.implemented_commands)
        implemented_count = len([c for c in self.implemented_commands.values() if c.implemented])
        unimplemented_count = len(self.unimplemented_commands)
        
        report.append("## 统计信息")
        report.append(f"- 总命令数: {total_commands}")
        report.append(f"- 已实现: {implemented_count}")
        report.append(f"- 未实现: {unimplemented_count}")
        implementation_rate = (implemented_count/total_commands*100) if total_commands > 0 else 0
        report.append(f"- 实现率: {implementation_rate:.1f}%")
        report.append("")
        
        # 已实现的命令
        report.append("## 已实现的命令")
        for command_name, command_info in self.implemented_commands.items():
            if command_info.implemented:
                status = "✅"
                issues_text = f" (问题: {', '.join(command_info.issues)})" if command_info.issues else ""
                report.append(f"- {status} /{command_name} - {command_info.description}{issues_text}")
        report.append("")
        
        # 未实现的命令
        if self.unimplemented_commands:
            report.append("## 未实现的命令")
            for command_name in self.unimplemented_commands:
                report.append(f"- ❌ /{command_name}")
            report.append("")
        
        # 建议移除的命令
        if self.unimplemented_commands:
            report.append("## 建议移除的命令")
            report.append("以下命令建议从帮助文档中移除，因为它们尚未实现:")
            for command_name in self.unimplemented_commands:
                report.append(f"- /{command_name}")
            report.append("")
        
        # 改进建议
        report.append("## 改进建议")
        report.append("1. 实现所有标记为未实现的命令")
        report.append("2. 为每个命令添加完整的错误处理")
        report.append("3. 统一命令的返回值格式")
        report.append("4. 添加命令参数验证")
        report.append("5. 改进命令的用户反馈信息")
        report.append("")
        
        return "\n".join(report)
    
    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run_analysis(self) -> None:
        """运行完整分析"""
        print("🚀 开始TUI命令实现状态分析")
        print("=" * 50)
        
        # 分析命令实现
        self.analyze_tui_commands()
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告
        report_file = f"tui_command_analysis_report_{self._get_current_time().replace(':', '-')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📊 分析完成！报告已保存到: {report_file}")
        
        # 显示简要统计
        total = len(self.implemented_commands)
        implemented = len([c for c in self.implemented_commands.values() if c.implemented])
        print(f"✅ 已实现: {implemented}/{total}")
        
        if self.unimplemented_commands:
            print(f"❌ 未实现: {len(self.unimplemented_commands)}")
            print("\n未实现的命令:")
            for cmd in self.unimplemented_commands:
                print(f"  - /{cmd}")
            
            # 询问是否更新帮助文本
            response = input("\n是否要更新帮助文本，移除未实现的命令? (y/n): ").strip().lower()
            if response == 'y':
                if self.update_help_text():
                    print("✅ 帮助文本已更新")
                else:
                    print("❌ 帮助文本更新失败")
        else:
            print("🎉 所有命令都已实现！")


def main():
    """主函数"""
    analyzer = TUICommandAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()