"""@Time    : 2025-08-05 10:00:00
@Author  : DAIP-LIVE Team
@File    : phase1_environment_test.py
@Description:
    Phase 1: 环境准备和基础验证测试
    包括Python环境检查、依赖服务验证等基础测试
"""

import json
import logging
import subprocess
import sys
import time
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase1_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnvironmentTester:
    """环境测试器"""
    
    def __init__(self):
        self.test_results = []
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "config.yaml"
        
    def add_test_result(self, test_name: str, status: str, details: str = "", execution_time: float = 0):
        """添加测试结果"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "execution_time": execution_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        logger.info(f"测试完成: {test_name} - {status}")
        if details:
            logger.info(f"详细信息: {details}")
    
    def run_test(self, test_func, test_name: str):
        """运行单个测试"""
        start_time = time.time()
        try:
            result = test_func()
            execution_time = time.time() - start_time
            if result:
                self.add_test_result(test_name, "PASS", f"执行时间: {execution_time:.2f}秒", execution_time)
                return True
            else:
                self.add_test_result(test_name, "FAIL", "测试返回False", execution_time)
                return False
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"异常: {str(e)}"
            self.add_test_result(test_name, "ERROR", error_msg, execution_time)
            logger.error(f"测试 {test_name} 异常: {e}")
            return False
    
    def test_python_version(self) -> bool:
        """测试Python版本"""
        logger.info("检查Python版本...")
        version = sys.version_info
        if version.major >= 3 and version.minor >= 10:
            logger.info(f"Python版本符合要求: {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            logger.error(f"Python版本过低: {version.major}.{version.minor}.{version.micro}, 需要3.10+")
            return False
    
    def test_required_packages(self) -> bool:
        """测试必需包安装"""
        logger.info("检查必需包安装...")
        required_packages = [
            'fastapi', 'uvicorn', 'pydantic', 'requests', 'ollama', 
            'chromadb', 'lona', 'pytest', 'selenium', 'playwright'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                logger.info(f"✓ {package} 已安装")
            except ImportError:
                logger.error(f"✗ {package} 未安装")
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"缺少包: {', '.join(missing_packages)}")
            return False
        return True
    
    def test_project_structure(self) -> bool:
        """测试项目结构"""
        logger.info("检查项目结构...")
        required_dirs = [
            'src', 'frontend', 'tests', 'templates', 'roles', 'data'
        ]
        
        required_files = [
            'pyproject.toml', 'config.yaml', 'CLAUDE.md'
        ]
        
        missing_items = []
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                logger.error(f"✗ 目录不存在: {dir_name}")
                missing_items.append(f"目录: {dir_name}")
            else:
                logger.info(f"✓ 目录存在: {dir_name}")
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                logger.error(f"✗ 文件不存在: {file_name}")
                missing_items.append(f"文件: {file_name}")
            else:
                logger.info(f"✓ 文件存在: {file_name}")
        
        if missing_items:
            logger.error(f"缺少项目结构: {', '.join(missing_items)}")
            return False
        return True
    
    def test_config_file(self) -> bool:
        """测试配置文件"""
        logger.info("检查配置文件...")
        if not self.config_file.exists():
            logger.error("配置文件不存在")
            return False
        
        try:
            import yaml
            with open(self.config_file, encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 检查关键配置项
            required_keys = ['llm', 'database', 'server']
            missing_keys = []
            
            for key in required_keys:
                if key not in config:
                    logger.error(f"✗ 配置项缺失: {key}")
                    missing_keys.append(key)
                else:
                    logger.info(f"✓ 配置项存在: {key}")
            
            if missing_keys:
                logger.error(f"配置文件缺少必要项: {', '.join(missing_keys)}")
                return False
            
            logger.info("配置文件验证通过")
            return True
            
        except Exception as e:
            logger.error(f"配置文件读取失败: {e}")
            return False
    
    def test_database_directory(self) -> bool:
        """测试数据库目录"""
        logger.info("检查数据库目录...")
        data_dir = self.project_root / "data"
        chroma_dir = data_dir / "chroma_db"
        
        if not data_dir.exists():
            logger.info("创建data目录")
            data_dir.mkdir(exist_ok=True)
        
        if not chroma_dir.exists():
            logger.info("创建chroma_db目录")
            chroma_dir.mkdir(exist_ok=True)
        
        logger.info("数据库目录准备完成")
        return True
    
    def test_ollama_service(self) -> bool:
        """测试Ollama服务"""
        logger.info("检查Ollama服务...")
        try:
            # 检查Ollama是否运行
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("✓ Ollama服务正常运行")
                return True
            else:
                logger.error("✗ Ollama服务未运行")
                return False
        except subprocess.TimeoutExpired:
            logger.error("✗ Ollama服务响应超时")
            return False
        except FileNotFoundError:
            logger.error("✗ Ollama未安装")
            return False
        except Exception as e:
            logger.error(f"✗ Ollama服务检查失败: {e}")
            return False
    
    def test_chromadb_connection(self) -> bool:
        """测试ChromaDB连接"""
        logger.info("检查ChromaDB连接...")
        try:
            import chromadb
            # 尝试连接到ChromaDB
            client = chromadb.PersistentClient(path=str(self.project_root / "data" / "chroma_db"))
            
            # 测试基本操作
            collection = client.get_or_create_collection("test_collection")
            collection.add(
                documents=["test document"],
                ids=["test_id"]
            )
            
            # 验证数据
            results = collection.get(ids=["test_id"])
            if len(results['documents']) > 0:
                logger.info("✓ ChromaDB连接正常")
                # 清理测试数据
                client.delete_collection("test_collection")
                return True
            else:
                logger.error("✗ ChromaDB数据读写失败")
                return False
                
        except Exception as e:
            logger.error(f"✗ ChromaDB连接失败: {e}")
            return False
    
    def test_network_ports(self) -> bool:
        """测试网络端口"""
        logger.info("检查网络端口...")
        import socket
        
        ports_to_check = [8000, 8080, 5000]
        available_ports = []
        
        for port in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                logger.info(f"✓ 端口 {port} 可用")
                available_ports.append(port)
            except OSError:
                logger.warning(f"✗ 端口 {port} 被占用")
        
        if len(available_ports) >= 2:
            logger.info(f"足够端口可用: {available_ports}")
            return True
        else:
            logger.error(f"可用端口不足: {available_ports}")
            return False
    
    def test_web_dependencies(self) -> bool:
        """测试Web相关依赖"""
        logger.info("检查Web相关依赖...")
        
        # 检查前端文件
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            logger.error("✗ frontend目录不存在")
            return False
        
        # 检查关键前端文件
        frontend_files = [
            "main_app.py", "components", "static", "templates"
        ]
        
        missing_files = []
        for file_name in frontend_files:
            file_path = frontend_dir / file_name
            if not file_path.exists():
                logger.error(f"✗ 前端文件不存在: {file_name}")
                missing_files.append(file_name)
            else:
                logger.info(f"✓ 前端文件存在: {file_name}")
        
        if missing_files:
            logger.error(f"缺少前端文件: {', '.join(missing_files)}")
            return False
        
        logger.info("Web依赖检查通过")
        return True
    
    def generate_report(self) -> str:
        """生成测试报告"""
        report_path = self.project_root / "phase1_test_report.json"
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        report = {
            "test_phase": "Phase 1: 环境准备和基础验证",
            "execution_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_results": self.test_results,
            "summary": {
                "status": "PASS" if passed_tests == total_tests else "FAIL",
                "issues": [r for r in self.test_results if r["status"] != "PASS"],
                "recommendations": self._generate_recommendations()
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"测试报告已生成: {report_path}")
        return str(report_path)
    
    def _generate_recommendations(self) -> list[str]:
        """生成建议"""
        recommendations = []
        
        for result in self.test_results:
            if result["status"] != "PASS":
                if "Python版本" in result["test_name"]:
                    recommendations.append("请升级Python到3.10或更高版本")
                elif "包" in result["test_name"]:
                    recommendations.append("请安装缺失的Python包")
                elif "配置文件" in result["test_name"]:
                    recommendations.append("请检查并完善配置文件")
                elif "Ollama" in result["test_name"]:
                    recommendations.append("请启动Ollama服务")
                elif "ChromaDB" in result["test_name"]:
                    recommendations.append("请检查ChromaDB安装和配置")
                elif "端口" in result["test_name"]:
                    recommendations.append("请释放被占用的端口")
        
        return recommendations
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        logger.info("开始Phase 1环境测试...")
        
        # 定义测试列表
        tests = [
            (self.test_python_version, "Python版本检查"),
            (self.test_required_packages, "必需包安装检查"),
            (self.test_project_structure, "项目结构检查"),
            (self.test_config_file, "配置文件检查"),
            (self.test_database_directory, "数据库目录检查"),
            (self.test_ollama_service, "Ollama服务检查"),
            (self.test_chromadb_connection, "ChromaDB连接检查"),
            (self.test_network_ports, "网络端口检查"),
            (self.test_web_dependencies, "Web依赖检查"),
        ]
        
        # 运行所有测试
        passed_count = 0
        for test_func, test_name in tests:
            if self.run_test(test_func, test_name):
                passed_count += 1
        
        # 生成报告
        report_path = self.generate_report()
        
        # 输出总结
        logger.info(f"Phase 1测试完成: {passed_count}/{len(tests)} 通过")
        logger.info(f"测试报告: {report_path}")
        
        return passed_count == len(tests)

def main():
    """主函数"""
    tester = EnvironmentTester()
    
    print("=" * 60)
    print("DAIP项目 Phase 1: 环境准备和基础验证测试")
    print("=" * 60)
    
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Phase 1测试全部通过！")
        print("可以继续进行Phase 2基础功能测试")
    else:
        print("\n❌ Phase 1测试存在问题")
        print("请查看测试报告并修复问题后重新测试")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())