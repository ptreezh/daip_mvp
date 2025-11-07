#!/usr/bin/env python3
"""
Test 1: Environment Validation
验证基础环境配置
"""

import sys
import os
import subprocess
import sqlite3

def test_python_version():
    """检查Python版本"""
    print("1. 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"   ✅ Python版本 {version.major}.{version.minor}.{version.micro} 符合要求")
        return True
    else:
        print(f"   ❌ Python版本 {version.major}.{version.minor}.{version.micro} 不符合要求（需要>=3.9）")
        return False

def test_project_structure():
    """检查项目结构"""
    print("2. 检查项目结构...")
    required_paths = [
        'src/daip_live',
        'roles',
        'docs',
        'config.yaml',
        'poetry.lock'
    ]
    
    missing_paths = []
    for path in required_paths:
        full_path = os.path.join(os.getcwd(), path)
        if not os.path.exists(full_path):
            missing_paths.append(path)
    
    if missing_paths:
        print(f"   ❌ 缺少以下路径: {missing_paths}")
        return False
    else:
        print("   ✅ 项目结构完整")
        return True

def test_config_file():
    """检查配置文件"""
    print("3. 检查配置文件...")
    config_path = os.path.join(os.getcwd(), 'config.yaml')
    if not os.path.exists(config_path):
        print("   ❌ config.yaml 文件不存在")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'database:' in content and 'llm_provider:' in content:
                print("   ✅ 配置文件格式正确")
                return True
            else:
                print("   ❌ 配置文件缺少必要字段")
                return False
    except Exception as e:
        print(f"   ❌ 读取配置文件失败: {e}")
        return False

def test_database_access():
    """检查数据库访问"""
    print("4. 检查数据库访问...")
    config_path = os.path.join(os.getcwd(), 'config.yaml')
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        db_path = config.get('database', {}).get('path', 'daip_live.db')
        if db_path == ':memory:':
            print("   ✅ 使用内存数据库")
            return True
        
        # 检查数据库文件
        if not os.path.exists(db_path):
            # 尝试在项目根目录查找
            root_db_path = os.path.join(os.getcwd(), db_path)
            if not os.path.exists(root_db_path):
                print(f"   ⚠️  数据库文件 {db_path} 不存在，将在首次访问时创建")
                return True
        
        # 尝试连接数据库
        conn = sqlite3.connect(db_path if os.path.exists(db_path) else ':memory:')
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        conn.close()
        print(f"   ✅ 数据库连接成功 (SQLite版本: {version})")
        return True
    except Exception as e:
        print(f"   ❌ 数据库访问失败: {e}")
        return False

def test_dependencies():
    """检查关键依赖"""
    print("5. 检查关键依赖...")
    required_packages = [
        'textual',
        'typer',
        'sqlalchemy',
        'pydantic',
        'yaml'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'yaml':
                import yaml
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"   ❌ 缺少以下依赖包: {missing_packages}")
        return False
    else:
        print("   ✅ 关键依赖包已安装")
        return True

def main():
    print("=" * 60)
    print("测试1: 基础环境验证")
    print("=" * 60)
    
    tests = [
        test_python_version,
        test_project_structure,
        test_config_file,
        test_database_access,
        test_dependencies
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ 测试 {test.__name__} 执行失败: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    if all(results):
        print("✅ 所有环境测试通过!")
        return 0
    else:
        failed_count = len([r for r in results if not r])
        print(f"❌ {failed_count} 个测试失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())