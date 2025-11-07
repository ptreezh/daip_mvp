#!/usr/bin/env python3
"""
Claude Code CLI - spec.kit integration
规范管理工具，用于创建和管理需求规格文档

这个工具为 Claude Code CLI 提供标准化的规范文档创建和管理功能，
特别针对软件开发项目的需求规格文档和计划文档。
"""

import os
import sys
import json
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import subprocess

__version__ = "1.0.0"
__author__ = "Claude Code CLI Integration"

@dataclass
class SpecTemplate:
    """规范模板"""
    name: str
    description: str
    category: str
    template_file: str
    schema_file: Optional[str] = None
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)

@dataclass
class SpecProject:
    """规范项目"""
    name: str
    description: str
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    specs: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)

class SpecKit:
    """规范管理工具主类"""

    def __init__(self, working_dir: str = "."):
        self.working_dir = Path(working_dir).resolve()
        self.spec_dir = self.working_dir / ".spec-kit"
        self.templates_dir = self.spec_dir / "templates"
        self.config_file = self.spec_dir / "config.yaml"
        self.project_file = self.spec_dir / "project.yaml"

        # 初始化目录结构
        self._init_directories()

        # 加载配置
        self.config = self._load_config()

        # 初始化默认模板
        self._init_default_templates()

    def _init_directories(self) -> None:
        """初始化目录结构"""
        self.spec_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        default_config = {
            "version": __version__,
            "default_author": "Claude Code",
            "default_language": "zh-CN",
            "output_format": "markdown",
            "auto_timestamp": True,
            "template_variables": {
                "project_name": "DAIP-LIVE",
                "company": "",
                "department": ""
            }
        }

        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)

        return default_config

    def _init_default_templates(self) -> None:
        """初始化默认模板"""
        templates = [
            SpecTemplate(
                name="requirements",
                description="软件需求规格文档模板",
                category="requirements",
                template_file="requirements.md.j2",
                required_fields=["project_name", "version", "description"],
                optional_fields=["scope", "stakeholders", "constraints"]
            ),
            SpecTemplate(
                name="implementation-plan",
                description="实施计划文档模板",
                category="planning",
                template_file="implementation_plan.md.j2",
                required_fields=["project_name", "timeline", "phases"],
                optional_fields=["risks", "dependencies", "milestones"]
            ),
            SpecTemplate(
                name="api-spec",
                description="API规格文档模板",
                category="technical",
                template_file="api_spec.md.j2",
                required_fields=["api_name", "version", "base_url"],
                optional_fields=["authentication", "rate_limiting", "examples"]
            ),
            SpecTemplate(
                name="system-architecture",
                description="系统架构设计文档模板",
                category="architecture",
                template_file="system_architecture.md.j2",
                required_fields=["system_name", "overview", "components"],
                optional_fields=["diagrams", "deployment", "monitoring"]
            )
        ]

        # 创建模板文件
        for template in templates:
            self._create_template_file(template)

    def _create_template_file(self, template: SpecTemplate) -> None:
        """创建模板文件"""
        template_path = self.templates_dir / template.template_file

        if template_path.exists():
            return

        template_content = self._get_template_content(template.name)

        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)

    def _get_template_content(self, template_name: str) -> str:
        """获取模板内容"""
        templates = {
            "requirements": '''# {{project_name}} - 需求规格文档

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| **项目名称** | {{project_name}} |
| **文档版本** | {{version}} |
| **创建日期** | {{created_date}} |
| **作者** | {{author}} |
| **状态** | {{status}} |

## 🎯 项目概述

### 项目背景
{{project_background}}

### 项目目标
{{project_goals}}

### 项目范围
{{scope}}

## 📊 功能需求

### 核心功能
{{core_features}}

### 扩展功能
{{extended_features}}

### 用户角色
{{user_roles}}

## 🔧 非功能需求

### 性能需求
{{performance_requirements}}

### 安全需求
{{security_requirements}}

### 可用性需求
{{usability_requirements}}

## 📋 验收标准

{{acceptance_criteria}}

## 📅 里程碑

{{milestones}}

---

*本文档由 spec.kit 自动生成*
''',

            "implementation-plan": '''# {{project_name}} - 实施计划

## 📋 项目信息

| 项目 | 内容 |
|------|------|
| **项目名称** | {{project_name}} |
| **计划版本** | {{version}} |
| **创建日期** | {{created_date}} |
| **项目经理** | {{manager}} |
| **预计工期** | {{duration}} |

## 🎯 实施概述

### 项目目标
{{project_objectives}}

### 实施策略
{{implementation_strategy}}

## 📅 实施阶段

{% for phase in phases %}
### {{phase.name}}
- **时间**: {{phase.start_date}} - {{phase.end_date}}
- **负责人**: {{phase.owner}}
- **主要任务**:
{% for task in phase.tasks %}
  - {{task}}
{% endfor %}

{% endfor %}

## 👥 团队分工

{{team_structure}}

## ⚠️ 风险管理

### 已识别风险
{{risks}}

### 缓解措施
{{mitigation_strategies}}

## 📊 进度跟踪

{{progress_tracking}}

## 🔗 依赖关系

{{dependencies}}

---

*本文档由 spec.kit 自动生成*
''',

            "api-spec": '''# {{api_name}} - API规格文档

## 📋 基本信息

| 项目 | 内容 |
|------|------|
| **API名称** | {{api_name}} |
| **版本** | {{version}} |
| **基础URL** | {{base_url}} |
| **创建日期** | {{created_date}} |
| **状态** | {{status}} |

## 🔐 认证方式

{{authentication}}

## 📡 端点列表

{% for endpoint in endpoints %}
### {{endpoint.method}} {{endpoint.path}}

**描述**: {{endpoint.description}}

**请求参数**:
{% for param in endpoint.parameters %}
- `{{param.name}}` ({{param.type}}) - {{param.description}}
{% endfor %}

**响应示例**:
```json
{{endpoint.response_example}}
```

{% endfor %}

## 🚫 错误码

{{error_codes}}

## 📊 限制说明

{{rate_limiting}}

## 🔗 SDK和工具

{{sdks_and_tools}}

---

*本文档由 spec.kit 自动生成*
''',

            "system-architecture": '''# {{system_name}} - 系统架构设计

## 📋 基本信息

| 项目 | 内容 |
|------|------|
| **系统名称** | {{system_name}} |
| **架构版本** | {{version}} |
| **创建日期** | {{created_date}} |
| **架构师** | {{architect}} |

## 🏗️ 架构概述

### 系统简介
{{overview}}

### 设计原则
{{design_principles}}

### 技术栈
{{tech_stack}}

## 🧩 组件设计

{% for component in components %}
### {{component.name}}

**职责**: {{component.responsibility}}

**技术实现**: {{component.technology}}

**接口**: {{component.interfaces}}

**依赖**: {{component.dependencies}}

{% endfor %}

## 🔄 数据流

{{data_flow}}

## 📐 部署架构

{{deployment}}

## 📊 监控和运维

{{monitoring}}

## 🔐 安全设计

{{security_design}}

## ⚡ 性能优化

{{performance_optimization}}

---

*本文档由 spec.kit 自动生成*
'''
        }

        return templates.get(template_name, "# 模板内容待定义")

    def init_project(self, name: str, description: str = "") -> None:
        """初始化规范项目"""
        project = SpecProject(
            name=name,
            description=description,
            config={
                "default_author": self.config.get("default_author", "Claude Code"),
                "output_dir": "specs",
                "template_dir": ".spec-kit/templates"
            }
        )

        with open(self.project_file, 'w', encoding='utf-8') as f:
            yaml.dump(project.__dict__, f, default_flow_style=False, allow_unicode=True)

        print(f"✅ 规范项目 '{name}' 初始化成功")
        print(f"📁 项目文件: {self.project_file}")
        print(f"📁 模板目录: {self.templates_dir}")

    def create_spec(self, template_name: str, output_file: str, **kwargs) -> None:
        """创建规范文档"""
        template_file = self.templates_dir / f"{template_name}.md.j2"

        if not template_file.exists():
            print(f"❌ 模板 '{template_name}' 不存在")
            return

        # 读取模板内容
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 准备模板变量
        variables = {
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "author": self.config.get("default_author", "Claude Code"),
            "project_name": self.config.get("template_variables", {}).get("project_name", ""),
            **kwargs
        }

        # 简单的模板替换（使用字符串格式化）
        try:
            rendered_content = template_content.format(**variables)
        except KeyError as e:
            print(f"❌ 缺少必需的模板变量: {e}")
            return

        # 确保输出目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_content)

        print(f"✅ 规范文档创建成功: {output_path}")

    def list_templates(self) -> None:
        """列出所有可用模板"""
        print("📋 可用模板:")
        print()

        template_files = list(self.templates_dir.glob("*.md.j2"))

        if not template_files:
            print("暂无可用模板")
            return

        for template_file in sorted(template_files):
            template_name = template_file.stem.replace(".md", "")
            print(f"  📄 {template_name}")

    def validate_spec(self, spec_file: str) -> None:
        """验证规范文档"""
        spec_path = Path(spec_file)

        if not spec_path.exists():
            print(f"❌ 规范文档不存在: {spec_file}")
            return

        # 简单的验证逻辑
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()

        issues = []

        # 检查必需章节
        required_sections = ["概述", "需求", "功能", "验收标准"]
        for section in required_sections:
            if section not in content:
                issues.append(f"缺少必需章节: {section}")

        if issues:
            print("❌ 验证失败:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ 规范文档验证通过")

    def status(self) -> None:
        """显示项目状态"""
        print("📊 spec.kit 项目状态")
        print("=" * 50)

        if self.project_file.exists():
            with open(self.project_file, 'r', encoding='utf-8') as f:
                project_data = yaml.safe_load(f)

            print(f"项目名称: {project_data.get('name', 'N/A')}")
            print(f"项目描述: {project_data.get('description', 'N/A')}")
            print(f"创建时间: {project_data.get('created_at', 'N/A')}")
            print(f"版本: {project_data.get('version', 'N/A')}")
        else:
            print("❌ 未找到项目文件，请先运行 'spec-kit init'")

        print()
        print(f"工作目录: {self.working_dir}")
        print(f"配置目录: {self.spec_dir}")
        print(f"模板目录: {self.templates_dir}")

        # 统计模板数量
        template_count = len(list(self.templates_dir.glob("*.md.j2")))
        print(f"可用模板: {template_count} 个")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Claude Code CLI - spec.kit 规范管理工具",
        prog="spec-kit"
    )

    parser.add_argument("--version", action="version", version=f"spec.kit {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化规范项目")
    init_parser.add_argument("name", help="项目名称")
    init_parser.add_argument("--description", "-d", default="", help="项目描述")

    # create 命令
    create_parser = subparsers.add_parser("create", help="创建规范文档")
    create_parser.add_argument("template", help="模板名称")
    create_parser.add_argument("output", help="输出文件路径")
    create_parser.add_argument("--var", "-v", action="append", help="模板变量 (key=value)")

    # list 命令
    subparsers.add_parser("list", help="列出所有可用模板")

    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="验证规范文档")
    validate_parser.add_argument("spec_file", help="规范文档路径")

    # status 命令
    subparsers.add_parser("status", help="显示项目状态")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 创建 SpecKit 实例
    spec_kit = SpecKit()

    # 执行命令
    try:
        if args.command == "init":
            spec_kit.init_project(args.name, args.description)

        elif args.command == "create":
            # 解析模板变量
            variables = {}
            if args.var:
                for var in args.var:
                    if "=" in var:
                        key, value = var.split("=", 1)
                        variables[key.strip()] = value.strip()

            spec_kit.create_spec(args.template, args.output, **variables)

        elif args.command == "list":
            spec_kit.list_templates()

        elif args.command == "validate":
            spec_kit.validate_spec(args.spec_file)

        elif args.command == "status":
            spec_kit.status()

    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()