#!/usr/bin/env python3
"""
替代测试运行器 - 用于无法安装Playwright的情况
提供手动测试指导和自动化HTML测试
"""

import os
import json
import time
from pathlib import Path

class AlternativeTestRunner:
    def __init__(self, base_dir="D:/daip/refactdoc/tutor"):
        self.base_dir = Path(base_dir)
        self.test_files = [
            "javascript验证.html",
            "简单交互测试.html", 
            "P1_SIX_DIMENSION_LEARNING_FIXED.html",
            "六向联动系统交互修复报告.html"
        ]
        self.test_results = []
        
    def check_file_exists(self, filename):
        """检查测试文件是否存在"""
        file_path = self.base_dir / filename
        exists = file_path.exists()
        size = file_path.stat().st_size if exists else 0
        return {
            "filename": filename,
            "exists": exists,
            "size": size,
            "path": str(file_path)
        }
    
    def analyze_html_structure(self, filename):
        """分析HTML文件结构"""
        try:
            file_path = self.base_dir / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "filename": filename,
                "has_javascript": "script" in content.lower(),
                "has_interactive_elements": any(x in content.lower() for x in [
                    "onclick", "onload", "onchange", "addEventListener"
                ]),
                "has_forms": "form" in content.lower(),
                "has_buttons": "button" in content.lower(),
                "has_test_classes": "test-" in content,
                "line_count": content.count('\n') + 1,
                "size_bytes": len(content)
            }
            return analysis
            
        except Exception as e:
            return {
                "filename": filename,
                "error": str(e),
                "has_javascript": False,
                "has_interactive_elements": False,
                "has_forms": False,
                "has_buttons": False,
                "has_test_classes": False,
                "line_count": 0,
                "size_bytes": 0
            }
    
    def generate_manual_test_guide(self):
        """生成手动测试指导"""
        guide = """
# 手动测试指导

## 测试文件列表

### 1. javascript验证.html
**测试目的**: 验证基础JavaScript交互功能
**测试步骤**:
1. 双击打开文件
2. 点击"测试DOM操作"按钮
3. 验证是否显示成功消息
4. 点击"测试AJAX请求"按钮
5. 验证是否显示成功消息
6. 检查控制台是否有错误

### 2. 简单交互测试.html
**测试目的**: 验证基本交互功能
**测试步骤**:
1. 双击打开文件
2. 点击"启动测试"按钮
3. 观察测试进度
4. 验证测试结果
5. 检查所有功能按钮

### 3. P1_SIX_DIMENSION_LEARNING_FIXED.html
**测试目的**: 验证六向联动系统修复效果
**测试步骤**:
1. 双击打开文件
2. 等待页面完全加载
3. 点击"FR-002"需求选择器
4. 验证是否切换到六向联动视图
5. 依次点击六个维度卡片：prompt、spec、design、plan、code、correlation
6. 验证维度切换是否正常
7. 点击导航栏按钮测试导航功能
8. 检查控制台错误

### 4. 六向联动系统交互修复报告.html
**测试目的**: 查看修复报告内容
**测试步骤**:
1. 双击打开文件
2. 查看修复历史
3. 验证问题列表
4. 检查解决方案

## 通用测试检查项

### JavaScript控制台检查
1. 按F12打开开发者工具
2. 切换到Console标签
3. 检查是否有红色错误信息
4. 记录所有错误信息

### 交互功能检查
1. 所有按钮是否可点击
2. 点击后是否有视觉反馈
3. 数据是否正确显示
4. 页面布局是否正常

### 性能检查
1. 页面加载时间是否合理（<3秒）
2. 交互响应是否及时（<1秒）
3. 内存使用是否正常
"""
        return guide
    
    def run_file_analysis(self):
        """运行文件分析"""
        print("🔍 开始文件分析...")
        
        for filename in self.test_files:
            print(f"\n📄 分析文件: {filename}")
            
            # 检查文件存在性
            file_info = self.check_file_exists(filename)
            print(f"  文件存在: {'✅' if file_info['exists'] else '❌'}")
            if file_info['exists']:
                print(f"  文件大小: {file_info['size']} bytes")
                print(f"  文件路径: {file_info['path']}")
            
            # 分析HTML结构
            if file_info['exists']:
                structure = self.analyze_html_structure(filename)
                print(f"  JavaScript: {'✅' if structure['has_javascript'] else '❌'}")
                print(f"  交互元素: {'✅' if structure['has_interactive_elements'] else '❌'}")
                print(f"  表单元素: {'✅' if structure['has_forms'] else '❌'}")
                print(f"  按钮元素: {'✅' if structure['has_buttons'] else '❌'}")
                print(f"  测试类: {'✅' if structure['has_test_classes'] else '❌'}")
                print(f"  代码行数: {structure['line_count']}")
                
                self.test_results.append({
                    "file_info": file_info,
                    "structure": structure
                })
        
        return self.test_results
    
    def generate_test_report(self):
        """生成测试报告"""
        report = {
            "timestamp": time.time(),
            "test_type": "alternative_test_runner",
            "files_analyzed": len(self.test_files),
            "results": self.test_results,
            "recommendations": self.get_recommendations()
        }
        
        # 保存报告
        report_file = self.base_dir / "alternative_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 测试报告已保存到: {report_file}")
        return report
    
    def get_recommendations(self):
        """获取测试建议"""
        recommendations = []
        
        for result in self.test_results:
            structure = result.get("structure", {})
            filename = result["file_info"]["filename"]
            
            if not structure.get("has_javascript", False):
                recommendations.append(f"{filename}: 缺少JavaScript代码")
            
            if not structure.get("has_interactive_elements", False):
                recommendations.append(f"{filename}: 缺少交互元素")
                
            if not structure.get("has_test_classes", False):
                recommendations.append(f"{filename}: 缺少测试标识")
        
        if not recommendations:
            recommendations.append("所有文件结构检查通过")
        
        return recommendations
    
    def run_complete_analysis(self):
        """运行完整分析"""
        print("🚀 开始替代测试分析...")
        print("="*50)
        
        # 运行文件分析
        results = self.run_file_analysis()
        
        # 生成手动测试指导
        guide = self.generate_manual_test_guide()
        guide_file = self.base_dir / "manual_test_guide.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
        print(f"\n📋 手动测试指导已保存到: {guide_file}")
        
        # 生成测试报告
        report = self.generate_test_report()
        
        # 输出总结
        print("\n" + "="*50)
        print("📊 分析完成总结:")
        print(f"  分析文件数量: {len(self.test_files)}")
        print(f"  存在文件数量: {len([r for r in results if r['file_info']['exists']])}")
        print(f"  有JavaScript文件: {len([r for r in results if r['structure'].get('has_javascript', False)])}")
        print(f"  有交互元素文件: {len([r for r in results if r['structure'].get('has_interactive_elements', False)])}")
        print("="*50)
        
        return report

def main():
    """主函数"""
    try:
        runner = AlternativeTestRunner()
        report = runner.run_complete_analysis()
        
        print("\n✅ 替代测试分析完成!")
        print("📝 建议:")
        print("1. 查看 manual_test_guide.md 进行手动测试")
        print("2. 查看 alternative_test_report.json 获取详细分析")
        print("3. 如果可以安装Playwright，请运行 playwright_interaction_test.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
