#!/usr/bin/env python3
"""角色清理工具

分析角色文件，处理过长和重复的角色名称：
1. 简化过长的角色名称
2. 合并重复的角色内容
3. 保留最完整的版本
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class RoleCleanupTool:
    """角色清理工具"""
    
    def __init__(self):
        self.roles_dir = Path("roles")
        self.role_files = []
        self.role_data = {}
        self.long_names = []
        self.duplicate_groups = []
        self.changes_made = []
    
    def analyze_roles(self):
        """分析角色文件"""
        print("🔍 分析角色文件...")
        
        # 收集所有角色文件
        self.role_files = list(self.roles_dir.glob("*.json"))
        print(f"发现 {len(self.role_files)} 个角色文件")
        
        # 加载角色数据
        for role_file in self.role_files:
            try:
                with open(role_file, encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 处理不同的数据格式
                if isinstance(data, list) and data:
                    data = data[0]  # 取第一个元素
                
                if isinstance(data, dict):
                    self.role_data[role_file.name] = {
                        'file_path': role_file,
                        'data': data,
                        'name': data.get('name', role_file.stem),
                        'description': data.get('description', ''),
                        'capabilities': data.get('capabilities', [])
                    }
                
            except Exception as e:
                print(f"⚠️ 无法加载 {role_file.name}: {e}")
        
        print(f"成功加载 {len(self.role_data)} 个角色")
        
        # 分析过长名称
        self.analyze_long_names()
        
        # 分析重复名称
        self.analyze_duplicate_names()
    
    def analyze_long_names(self):
        """分析过长的角色名称"""
        print("\n🔍 分析过长的角色名称...")
        
        for file_name, role_info in self.role_data.items():
            name = role_info['name']
            if len(name) > 80:
                self.long_names.append({
                    'file_name': file_name,
                    'name': name,
                    'length': len(name),
                    'suggested_name': self.suggest_short_name(name)
                })
        
        if self.long_names:
            print(f"发现 {len(self.long_names)} 个过长的角色名称:")
            for item in self.long_names:
                print(f"  📝 {item['file_name']}")
                print(f"     原名: {item['name'][:60]}... ({item['length']}字符)")
                print(f"     建议: {item['suggested_name']}")
                print()
        else:
            print("✅ 没有发现过长的角色名称")
    
    def suggest_short_name(self, long_name: str) -> str:
        """建议简化的角色名称"""
        # 移除常见的冗余词汇
        redundant_words = [
            "Agent Role:", "Agent Role The", "**Agent Role:**", 
            "The", "A", "An", "Senior Editor", "Specialist",
            "Practitioner", "Analyst", "Researcher", "Expert"
        ]
        
        name = long_name
        for word in redundant_words:
            name = name.replace(word, "").strip()
        
        # 移除多余的标点和空格
        name = " ".join(name.split())
        name = name.replace("**", "").replace("(", "").replace(")", "")
        name = name.replace("'s", "").strip()
        
        # 如果还是太长，取前50个字符
        if len(name) > 50:
            name = name[:47] + "..."
        
        return name or "Unknown Role"
    
    def analyze_duplicate_names(self):
        """分析重复的角色名称"""
        print("\n🔍 分析重复的角色名称...")
        
        # 按名称分组
        name_groups = defaultdict(list)
        for file_name, role_info in self.role_data.items():
            name = role_info['name'].strip().lower()
            name_groups[name].append((file_name, role_info))
        
        # 找出重复的组
        for name, roles in name_groups.items():
            if len(roles) > 1:
                self.duplicate_groups.append({
                    'name': name,
                    'roles': roles,
                    'count': len(roles)
                })
        
        if self.duplicate_groups:
            print(f"发现 {len(self.duplicate_groups)} 组重复的角色名称:")
            for group in self.duplicate_groups:
                print(f"  🔄 '{group['name']}' ({group['count']}个重复)")
                for file_name, role_info in group['roles']:
                    desc_preview = role_info['description'][:50] + "..." if len(role_info['description']) > 50 else role_info['description']
                    print(f"     - {file_name}: {desc_preview}")
                print()
        else:
            print("✅ 没有发现重复的角色名称")
    
    def fix_long_names(self):
        """修复过长的角色名称"""
        if not self.long_names:
            return
        
        print("\n🔧 修复过长的角色名称...")
        
        for item in self.long_names:
            file_name = item['file_name']
            role_info = self.role_data[file_name]
            old_name = role_info['name']
            new_name = item['suggested_name']
            
            # 更新角色数据
            role_info['data']['name'] = new_name
            
            # 保存文件
            try:
                with open(role_info['file_path'], 'w', encoding='utf-8') as f:
                    json.dump(role_info['data'], f, indent=2, ensure_ascii=False)
                
                self.changes_made.append(f"简化名称: {file_name}")
                print(f"✅ 已简化: {file_name}")
                print(f"   {old_name[:50]}... → {new_name}")
                
            except Exception as e:
                print(f"❌ 修复失败 {file_name}: {e}")
    
    def merge_duplicate_roles(self):
        """合并重复的角色"""
        if not self.duplicate_groups:
            return
        
        print("\n🔧 合并重复的角色...")
        
        for group in self.duplicate_groups:
            print(f"\n处理重复组: '{group['name']}'")
            
            # 分析每个角色的完整性
            roles_analysis = []
            for file_name, role_info in group['roles']:
                completeness_score = self.calculate_completeness_score(role_info['data'])
                roles_analysis.append({
                    'file_name': file_name,
                    'role_info': role_info,
                    'completeness_score': completeness_score
                })
            
            # 按完整性排序，选择最完整的作为主角色
            roles_analysis.sort(key=lambda x: x['completeness_score'], reverse=True)
            primary_role = roles_analysis[0]
            secondary_roles = roles_analysis[1:]
            
            print(f"  主角色: {primary_role['file_name']} (完整性: {primary_role['completeness_score']:.2f})")
            
            # 合并其他角色的内容到主角色
            merged_data = self.merge_role_data(primary_role['role_info']['data'], 
                                             [r['role_info']['data'] for r in secondary_roles])
            
            # 保存合并后的主角色
            try:
                with open(primary_role['role_info']['file_path'], 'w', encoding='utf-8') as f:
                    json.dump(merged_data, f, indent=2, ensure_ascii=False)
                
                print(f"  ✅ 已更新主角色: {primary_role['file_name']}")
                
                # 删除重复的角色文件
                for secondary_role in secondary_roles:
                    try:
                        secondary_role['role_info']['file_path'].unlink()
                        print(f"  🗑️ 已删除重复文件: {secondary_role['file_name']}")
                        self.changes_made.append(f"删除重复: {secondary_role['file_name']}")
                    except Exception as e:
                        print(f"  ❌ 删除失败 {secondary_role['file_name']}: {e}")
                
                self.changes_made.append(f"合并重复角色: {group['name']}")
                
            except Exception as e:
                print(f"  ❌ 合并失败: {e}")
    
    def calculate_completeness_score(self, role_data: dict[str, Any]) -> float:
        """计算角色数据的完整性分数"""
        score = 0.0
        
        # 基础字段权重
        if role_data.get('name'):
            score += 1.0
        if role_data.get('description'):
            score += 2.0 * min(len(role_data['description']) / 200, 1.0)  # 描述长度
        if role_data.get('system_prompt'):
            score += 2.0 * min(len(role_data['system_prompt']) / 500, 1.0)  # 系统提示长度
        if role_data.get('capabilities'):
            score += 1.0 * min(len(role_data['capabilities']) / 5, 1.0)  # 能力数量
        
        # 额外字段加分
        extra_fields = ['expertise', 'values', 'reasoning_style', 'examples']
        for field in extra_fields:
            if role_data.get(field):
                score += 0.5
        
        return score
    
    def merge_role_data(self, primary_data: dict[str, Any], secondary_data_list: list[dict[str, Any]]) -> dict[str, Any]:
        """合并角色数据"""
        merged = primary_data.copy()
        
        for secondary_data in secondary_data_list:
            # 合并描述（如果主角色描述较短）
            if len(secondary_data.get('description', '')) > len(merged.get('description', '')):
                merged['description'] = secondary_data['description']
            
            # 合并系统提示（如果主角色提示较短）
            if len(secondary_data.get('system_prompt', '')) > len(merged.get('system_prompt', '')):
                merged['system_prompt'] = secondary_data['system_prompt']
            
            # 合并能力列表
            if 'capabilities' in secondary_data:
                primary_capabilities = set(merged.get('capabilities', []))
                secondary_capabilities = set(secondary_data['capabilities'])
                merged['capabilities'] = list(primary_capabilities | secondary_capabilities)
            
            # 合并其他有用字段
            for field in ['expertise', 'values', 'reasoning_style']:
                if field in secondary_data and field not in merged:
                    merged[field] = secondary_data[field]
                elif field in secondary_data and isinstance(merged.get(field), list) and isinstance(secondary_data[field], list):
                    merged[field] = list(set(merged[field] + secondary_data[field]))
        
        return merged
    
    def generate_report(self):
        """生成清理报告"""
        print("\n" + "=" * 50)
        print("📊 角色清理报告")
        print("=" * 50)
        
        print(f"总角色文件: {len(self.role_files)}")
        print(f"成功加载: {len(self.role_data)}")
        print(f"过长名称: {len(self.long_names)}")
        print(f"重复组数: {len(self.duplicate_groups)}")
        print(f"执行更改: {len(self.changes_made)}")
        
        if self.changes_made:
            print("\n🔧 执行的更改:")
            for change in self.changes_made:
                print(f"  • {change}")
        
        # 保存清理报告
        report = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'total_files': len(self.role_files),
            'loaded_roles': len(self.role_data),
            'long_names_found': len(self.long_names),
            'duplicate_groups_found': len(self.duplicate_groups),
            'changes_made': self.changes_made,
            'long_names_details': self.long_names,
            'duplicate_groups_details': [
                {
                    'name': group['name'],
                    'count': group['count'],
                    'files': [role[0] for role in group['roles']]
                }
                for group in self.duplicate_groups
            ]
        }
        
        report_file = Path("role_cleanup_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
    
    def run_cleanup(self):
        """运行完整的清理流程"""
        print("🧹 启动角色清理工具")
        print("=" * 50)
        
        # 分析角色
        self.analyze_roles()
        
        # 修复过长名称
        self.fix_long_names()
        
        # 合并重复角色
        self.merge_duplicate_roles()
        
        # 生成报告
        self.generate_report()
        
        print("\n🎉 角色清理完成！")
        if self.changes_made:
            print("建议重新运行系统分析以验证修复效果。")


def main():
    """主函数"""
    cleanup_tool = RoleCleanupTool()
    
    try:
        cleanup_tool.run_cleanup()
        return True
    except Exception as e:
        print(f"❌ 清理过程异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 清理被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 清理异常: {e}")
        sys.exit(1)