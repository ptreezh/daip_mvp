#!/usr/bin/env python3
"""批量修复角色定义文件
确保所有角色文件都有必需的字段
"""

import hashlib
import json
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_id_from_name(name: str) -> str:
    """从角色名称生成ID"""
    return hashlib.md5(name.encode()).hexdigest()[:16]

def fix_role_file(file_path: Path) -> bool:
    """修复单个角色文件"""
    try:
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
        
        # 跳过非角色文件（如统计文件）
        if file_path.name in ['role_statistics.json', 'user_defined_roles.json']:
            logger.info(f"跳过特殊文件: {file_path.name}")
            return True
        
        # 检查并修复必需字段
        modified = False
        
        # 修复缺少的id字段
        if 'id' not in data or not data['id']:
            if 'name' in data:
                data['id'] = generate_id_from_name(data['name'])
                modified = True
                logger.info(f"为 {file_path.name} 生成ID: {data['id']}")
            else:
                logger.error(f"文件 {file_path.name} 缺少name字段，无法生成ID")
                return False
        
        # 修复缺少的name字段
        if 'name' not in data or not data['name']:
            data['name'] = file_path.stem  # 使用文件名作为角色名
            modified = True
            logger.info(f"为 {file_path.name} 设置name: {data['name']}")
        
        # 修复缺少的description字段
        if 'description' not in data or not data['description']:
            data['description'] = f"Role: {data['name']}"
            modified = True
            logger.info(f"为 {file_path.name} 设置默认description")
        
        # 修复缺少的system_prompt字段
        if 'system_prompt' not in data or not data['system_prompt']:
            # 尝试从description生成system_prompt
            description = data.get('description', '')
            if description:
                data['system_prompt'] = f"你是{data['name']}。{description[:200]}..."
            else:
                data['system_prompt'] = f"你是{data['name']}，一个专业的AI助手。"
            modified = True
            logger.info(f"为 {file_path.name} 生成system_prompt")
        
        # 修复capabilities字段
        if 'capabilities' not in data:
            data['capabilities'] = []
            modified = True
            logger.info(f"为 {file_path.name} 设置空capabilities")
        elif not isinstance(data['capabilities'], (list, dict)):
            # 如果capabilities不是列表或字典，转换为空列表
            data['capabilities'] = []
            modified = True
            logger.info(f"修复 {file_path.name} 的capabilities格式")
        
        # 如果有修改，保存文件
        if modified:
            # 创建备份
            backup_path = file_path.with_suffix('.json.backup')
            if not backup_path.exists():
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 保存修复后的文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 修复完成: {file_path.name}")
        else:
            logger.info(f"✓ 无需修复: {file_path.name}")
        
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON格式错误 {file_path.name}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 修复失败 {file_path.name}: {e}")
        return False

def main():
    """主函数"""
    roles_dir = Path("roles")
    
    if not roles_dir.exists():
        logger.error("roles目录不存在")
        return False
    
    logger.info("🚀 开始批量修复角色定义文件")
    
    # 获取所有JSON文件
    json_files = list(roles_dir.glob("*.json"))
    logger.info(f"找到 {len(json_files)} 个JSON文件")
    
    success_count = 0
    error_count = 0
    
    for json_file in json_files:
        logger.info(f"\n📋 处理文件: {json_file.name}")
        
        if fix_role_file(json_file):
            success_count += 1
        else:
            error_count += 1
    
    # 总结
    logger.info("\n📊 修复完成:")
    logger.info(f"   成功: {success_count} 个文件")
    logger.info(f"   失败: {error_count} 个文件")
    logger.info(f"   总计: {len(json_files)} 个文件")
    
    if error_count == 0:
        logger.info("✅ 所有文件修复成功！")
        return True
    else:
        logger.warning(f"⚠️ {error_count} 个文件修复失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)