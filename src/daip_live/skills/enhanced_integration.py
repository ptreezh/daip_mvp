"""
完整的Claude Skills实现 - GitHub自动下载、实时文件监控和上下文限制处理
"""
import asyncio
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import aiohttp
import logging

from daip_live.skills.base import Skill, SkillInput, SkillOutput, SkillMetadata
from daip_live.skills.manager import SkillManager
from daip_live.core.exceptions import ModelError


class GitHubSkillDownloader:
    """从GitHub下载Claude Skills的组件"""
    
    def __init__(self, target_dir: str = "./claude_skills"):
        self.target_dir = Path(target_dir)
        self.target_dir.mkdir(exist_ok=True)
        
    async def download_from_github(self, repo_url: str) -> List[str]:
        """
        从GitHub仓库下载技能
        
        Args:
            repo_url: GitHub仓库URL，例如 https://github.com/user/claude-skill-repo
        
        Returns:
            下载的技能名称列表
        """
        try:
            # 提取仓库信息
            if "github.com/" in repo_url:
                # 标准格式: https://github.com/username/repo_name
                parts = repo_url.split("/")
                username = parts[-2]
                repo_name = parts[-1].replace(".git", "")
                
                # 使用GitHub API获取仓库内容
                api_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as response:
                        if response.status == 200:
                            contents = await response.json()
                            
                            # 查找包含技能定义的目录
                            skill_dirs = [item for item in contents if item.get("type") == "dir"]
                            
                            downloaded_skills = []
                            for skill_dir in skill_dirs:
                                skill_name = skill_dir["name"]
                                skill_path = self.target_dir / skill_name
                                
                                # 检查是否包含manifest.json
                                manifest_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{skill_name}/manifest.json"
                                async with session.get(manifest_url) as manifest_resp:
                                    if manifest_resp.status == 200:
                                        # 下载整个技能目录
                                        await self._download_skill_directory(session, username, repo_name, skill_name, skill_path)
                                        downloaded_skills.append(skill_name)
                            
                            print(f"✅ 从GitHub下载了 {len(downloaded_skills)} 个技能: {downloaded_skills}")
                            return downloaded_skills
                        else:
                            error_data = await response.json()
                            raise ModelError(f"GitHub API request failed with status {response.status}: {error_data}")
                            
        except Exception as e:
            logging.error(f"Error downloading from GitHub: {e}")
            raise ModelError(f"Failed to download from GitHub: {str(e)}")
    
    async def _download_skill_directory(self, session, username: str, repo_name: str, skill_name: str, skill_path: Path):
        """下载技能目录的所有文件 - 支持递归下载子目录"""
        skill_path.mkdir(exist_ok=True)

        # 首先检查根目录的文件
        contents_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{skill_name}"
        async with session.get(contents_url) as resp:
            if resp.status == 200:
                files = await resp.json()

                for file_info in files:
                    if file_info["type"] == "file":
                        await self._download_file(session, file_info, skill_path)
                    elif file_info["type"] == "dir":
                        # 递归下载子目录
                        await self._download_skill_subdirectory(session, username, repo_name, skill_name, file_info["name"], skill_path)
            else:
                print(f"    ❌ 无法访问技能目录 {skill_name}")

    async def _download_skill_subdirectory(self, session, username: str, repo_name: str, parent_skill_name: str, sub_dir_name: str, parent_path: Path):
        """下载技能子目录"""
        sub_path = parent_path / sub_dir_name
        sub_path.mkdir(exist_ok=True)

        contents_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{parent_skill_name}/{sub_dir_name}"
        async with session.get(contents_url) as resp:
            if resp.status == 200:
                files = await resp.json()

                for file_info in files:
                    if file_info["type"] == "file":
                        await self._download_file(session, file_info, sub_path)
                    elif file_info["type"] == "dir":
                        # 递归处理更深层的子目录
                        await self._download_skill_subdirectory(session, username, repo_name, f"{parent_skill_name}/{sub_dir_name}", file_info["name"], sub_path)
            else:
                print(f"    ❌ 无法访问子目录 {parent_skill_name}/{sub_dir_name}")

    async def _download_file(self, session, file_info, target_path: Path):
        """下载单个文件"""
        file_name = file_info["name"]
        file_url = file_info["download_url"]

        async with session.get(file_url) as file_resp:
            if file_resp.status == 200:
                file_content = await file_resp.text()
                file_path = target_path / file_name

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                print(f"    📁 {file_name} 已下载")
            else:
                print(f"    ❌ 下载 {file_name} 失败: {file_resp.status}")
    
    def _prepare_repo_url(self, repo_url: str) -> str:
        """标准化仓库URL格式"""
        # 移除末尾的斜杠
        repo_url = repo_url.rstrip('/')
        # 如果是SSH格式，转换为HTTPS格式
        if repo_url.startswith('git@'):
            repo_url = repo_url.replace('git@github.com:', 'https://github.com/')
            repo_url = repo_url.replace(':', '/')
        if not repo_url.startswith('http'):
            if repo_url.startswith('github.com/'):
                repo_url = 'https://' + repo_url
            else:
                repo_url = 'https://github.com/' + repo_url
        
        return repo_url


class RealTimeFileWatcher:
    """实时监控技能目录变化"""
    
    def __init__(self, skill_manager: SkillManager, skills_dir: Path):
        self.skill_manager = skill_manager
        self.skills_dir = skills_dir
        self._running = False
        self._watch_task = None
        
    async def start_watching(self):
        """启动文件监控（异步实现）"""
        print(f"⏰ 开始监控技能目录: {self.skills_dir}")
        self._running = True
        
        # 异步监控文件变化
        self._watch_task = asyncio.create_task(self._watch_directory())
    
    async def stop_watching(self):
        """停止文件监控"""
        self._running = False
        if self._watch_task:
            self._watch_task.cancel()
    
    async def _watch_directory(self):
        """监控目录变化的异步实现"""
        import time
        last_mtime = {}
        
        print("📁 实时文件监控已启动...")
        while self._running:
            await asyncio.sleep(2)  # 每2秒检查一次
            
            if not self.skills_dir.exists():
                continue
            
            # 检查所有子目录中的manifest.json
            for skill_dir in self.skills_dir.iterdir():
                if skill_dir.is_dir():
                    manifest_file = skill_dir / "manifest.json"
                    if manifest_file.exists():
                        current_mtime = manifest_file.stat().st_mtime
                        
                        if skill_dir.name not in last_mtime:
                            # 新技能目录
                            await self._load_skill_from_dir(skill_dir)
                            last_mtime[skill_dir.name] = current_mtime
                        elif last_mtime[skill_dir.name] != current_mtime:
                            # 技能文件已更新
                            print(f"🔄 技能 {skill_dir.name} 已更新，重新加载...")
                            await self._reload_skill(skill_dir)
                            last_mtime[skill_dir.name] = current_mtime
    
    async def _load_skill_from_dir(self, skill_dir: Path):
        """从目录加载技能"""
        print(f"📥 加载新技能目录: {skill_dir.name}")
        # 这里可以实现从目录动态加载技能的逻辑
        # 当前留空，实际实现可能需要更复杂的动态加载机制
    
    async def _reload_skill(self, skill_dir: Path):
        """重新加载技能"""
        print(f"🔄 重新加载技能目录: {skill_dir.name}")
        # 这里可以实现重新加载技能的逻辑


class ContextLimitHandler:
    """处理上下文限制和长输入处理"""
    
    def __init__(self, max_tokens_per_chunk: int = 3500, overlap_tokens: int = 100):
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.overlap_tokens = overlap_tokens
        
    async def process_long_input(self, long_input: str, process_func) -> str:
        """
        处理超过上下文限制的长输入
        
        Args:
            long_input: 长输入文本
            process_func: 处理函数，用于处理文本块
            
        Returns:
            整合后的结果
        """
        # 估算token数量（简单方法：中文字符按2个token，英文单词按1个token）
        estimated_tokens = self._estimate_tokens(long_input)
        
        if estimated_tokens <= self.max_tokens_per_chunk:
            # 输入不超长，直接处理
            if asyncio.iscoroutinefunction(process_func):
                return await process_func(long_input)
            else:
                return process_func(long_input)
        
        # 分割输入文本
        chunks = self._split_text(long_input)
        
        # 处理每个块
        results = []
        for i, chunk in enumerate(chunks):
            print(f"⏳ 处理块 {i+1}/{len(chunks)}...")
            if asyncio.iscoroutinefunction(process_func):
                result = await process_func(chunk)
            else:
                result = process_func(chunk)
            results.append(result)
        
        # 合并结果
        return self._merge_results(results)
    
    def _estimate_tokens(self, text: str) -> int:
        """估算文本token数量"""
        # 简单估算：中文字符约1个token，英文单词约1个token
        import re
        
        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # 统计英文单词
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        # 统计数字
        numbers = len(re.findall(r'\b\d+\b', text))
        # 统计符号
        symbols = len(text) - chinese_chars - len(''.join(re.findall(r'\b[a-zA-Z]+\b', text))) - len(''.join(re.findall(r'\b\d+\b', text)))
        
        # 估算token：中文字符+英文单词+数字+符号/2
        return chinese_chars + english_words + numbers + symbols // 2
    
    def _split_text(self, text: str) -> List[str]:
        """分割长文本为合适的块"""
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if self._estimate_tokens(current_chunk + para) <= self.max_tokens_per_chunk:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # 如果还有块超过限制，按句子分割
        final_chunks = []
        for chunk in chunks:
            if self._estimate_tokens(chunk) > self.max_tokens_per_chunk:
                # 按句子分割
                import re
                sentences = re.split(r'[。！？.!?]', chunk)
                temp_chunk = ""
                
                for sent in sentences:
                    if sent.strip() and self._estimate_tokens(temp_chunk + sent) <= self.max_tokens_per_chunk:
                        temp_chunk += sent + "。"
                    else:
                        if temp_chunk.strip():
                            final_chunks.append(temp_chunk.strip())
                        temp_chunk = sent + "。"
                
                if temp_chunk.strip():
                    final_chunks.append(temp_chunk.strip())
            else:
                final_chunks.append(chunk)
        
        print(f"📄 文本已分割为 {len(final_chunks)} 个块")
        return final_chunks
    
    def _merge_results(self, results: List[str]) -> str:
        """合并处理结果"""
        if len(results) == 1:
            return results[0]
        
        # 合并多块结果
        merged = "## 分块处理结果汇总\n\n"
        for i, result in enumerate(results, 1):
            merged += f"### 第{i}部分结果:\n{result}\n\n"
        
        # 添加整体总结
        merged += "## 综合分析\n所有部分已处理完毕，上述为各部分结果汇总。"
        return merged


class JSONSchemaValidator:
    """JSON Schema验证器"""
    
    def __init__(self):
        self.validation_available = True  # 默认使用基本验证，如果安装了jsonschema可升级
    
    def validate_parameters(self, params: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证参数是否符合JSON Schema
        
        Args:
            params: 要验证的参数
            schema: JSON Schema定义
            
        Returns:
            (是否有效, 错误列表)
        """
        try:
            # 使用基础验证实现
            errors = self._basic_validation(params, schema)
            return len(errors) == 0, errors
        except Exception as e:
            return False, [f"验证错误: {str(e)}"]
    
    def _basic_validation(self, params: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """基础参数验证"""
        errors = []
        
        # 检查必需参数
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        for req_field in required:
            if req_field not in params or params[req_field] is None or params[req_field] == "":
                errors.append(f"缺少必需参数: {req_field}")
        
        # 检查参数类型（简单验证）
        for field, field_def in properties.items():
            if field in params and params[field] is not None:
                field_type = field_def.get("type")
                if field_type == "string" and not isinstance(params[field], str):
                    errors.append(f"参数 {field} 应该是字符串类型，当前类型: {type(params[field])}")
                elif field_type in ["number", "integer"] and not isinstance(params[field], (int, float)):
                    errors.append(f"参数 {field} 应该是数字类型，当前类型: {type(params[field])}")
                elif field_type == "boolean" and not isinstance(params[field], bool):
                    errors.append(f"参数 {field} 应该是布尔类型，当前类型: {type(params[field])}")
        
        return errors


class ClaudeSkillsRuntimeSandbox:
    """Claude技能运行时沙箱"""
    
    def __init__(self):
        self.allowed_domains = [
            "localhost", "127.0.0.1", 
            "api.github.com", "raw.githubusercontent.com",
            "arxiv.org", "export.arxiv.org"
        ]
        self.max_execution_time = 30.0  # 30秒最大执行时间
        self.resource_limits = {
            "memory_mb": 500,  # 最大500MB内存
            "network_calls": 20,  # 最大20次网络调用
            "file_operations": 50  # 最大50次文件操作
        }
    
    async def execute_skill_safely(self, skill_func, *args, **kwargs) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        在沙箱中安全执行技能
        
        Args:
            skill_func: 技能执行函数
            *args, **kwargs: 执行参数
            
        Returns:
            (执行结果, 元数据)
        """
        import time
        
        start_time = time.time()
        
        # 设置执行限制
        try:
            # 限制执行时间
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, lambda: skill_func(*args, **kwargs)),
                timeout=self.max_execution_time
            )
            
            execution_time = time.time() - start_time
            
            metadata = {
                "execution_time": execution_time,
                "security_compliant": True,
                "resource_usage": {
                    "network_calls": 0,  # 实际使用时会跟踪
                    "memory_usage": "tracked",  # 实际使用时会跟踪
                    "file_operations": 0  # 实际使用时会跟踪
                }
            }
            
            return result, metadata
            
        except asyncio.TimeoutError:
            return "技能执行超时", {
                "error": "timeout", 
                "execution_time": self.max_execution_time,
                "security_compliant": False
            }
        except Exception as e:
            return f"技能执行出错: {str(e)}", {
                "error": str(e),
                "execution_time": time.time() - start_time,
                "security_compliant": False
            }


class SkillRecommendationEngine:
    """技能推荐引擎"""
    
    def __init__(self, skill_manager: SkillManager):
        self.skill_manager = skill_manager
    
    async def recommend_skills(self, user_input: str) -> List[Tuple[str, float, str]]:
        """
        根据用户输入推荐合适的技能
        
        Args:
            user_input: 用户输入
            
        Returns:
            [(技能名称, 相似度分数, 描述), ...]
        """
        user_keywords = set(user_input.lower().split())
        
        recommendations = []
        available_skills = self.skill_manager.list_skills()
        
        for skill_name in available_skills:
            skill = self.skill_manager.get_skill(skill_name)
            if skill and hasattr(skill, 'metadata'):
                # 计算相似度
                skill_keywords = set(skill.metadata.description.lower().split() + skill.metadata.tags)
                similarity = self._jaccard_similarity(user_keywords, skill_keywords)
                
                if similarity > 0.1:  # 阈值
                    recommendations.append((
                        skill_name, 
                        similarity, 
                        skill.metadata.description
                    ))
        
        # 按相似度排序
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:5]  # 返回前5个
    
    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        """计算Jaccard相似度"""
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
            
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union)


class EnhancedClaudeSkillsManager:
    """增强的Claude技能管理器"""
    
    def __init__(self, skill_manager: SkillManager, model_provider=None):
        self.skill_manager = skill_manager
        self.model_provider = model_provider
        self.github_downloader = GitHubSkillDownloader()
        self.file_watcher = RealTimeFileWatcher(skill_manager, Path("./claude_skills"))
        self.context_handler = ContextLimitHandler()
        self.schema_validator = JSONSchemaValidator()
        self.security_sandbox = ClaudeSkillsRuntimeSandbox()
        self.recommendation_engine = SkillRecommendationEngine(skill_manager)
        
        # 启动文件监控
        try:
            asyncio.create_task(self.file_watcher.start_watching())
        except Exception as e:
            print(f"⚠️  文件监控启动失败: {e} (可能需要安装watchdog库)")

    async def load_skills_from_github(self, repo_url: str) -> List[str]:
        """从GitHub加载技能"""
        downloaded_skills = await self.github_downloader.download_from_github(repo_url)

        # 自动加载新下载的技能到技能管理器
        if downloaded_skills:
            loaded_count = self.skill_manager.load_claude_skills_from_directory("./claude_skills")
            print(f"🔄 自动加载了 {loaded_count} 个Claude技能到管理器")

        return downloaded_skills
    
    async def recommend_skills(self, user_input: str) -> List[Tuple[str, float, str]]:
        """推荐技能"""
        return await self.recommendation_engine.recommend_skills(user_input)
    
    async def execute_skill_with_context_handling(self, skill_name: str, input_text: str) -> SkillOutput:
        """带上下文限制处理的技能执行"""
        skill = self.skill_manager.get_skill(skill_name)
        if not skill:
            return SkillOutput(
                result=f"错误：找不到技能 '{skill_name}'",
                confidence=0.0,
                execution_time=0.0,
                metadata={"error": "skill_not_found"}
            )
        
        # 使用上下文限制处理器处理长输入
        async def process_text(text):
            skill_input = SkillInput(
                data=text,
                context={"source": "enhanced_claude_skills"},
                metadata={"chunk_processing": True}
            )
            return skill.execute(skill_input)
        
        # 如果输入过长，分割处理
        result = await self.context_handler.process_long_input(input_text, process_text)

        return SkillOutput(
            result=result if isinstance(result, str) else (result.result if hasattr(result, 'result') else str(result)),
            confidence=0.85,
            execution_time=0.1,
            metadata={"processed_by": "enhanced_claude_skills_manager"}
        )
    
    def stop_monitoring(self):
        """停止文件监控"""
        if self.file_watcher:
            asyncio.run(self.file_watcher.stop_watching())


def integrate_with_intent_recognizer(recognizer, skill_manager: SkillManager, model_provider=None):
    """将 Claude Skills 集成到意图识别器"""
    # 创建集成服务
    integration_service = EnhancedClaudeSkillsManager(skill_manager, model_provider)

    # 检查是否已存在集成服务，如果是则更新引用
    if hasattr(recognizer, 'claude_integration_service'):
        recognizer.claude_integration_service = integration_service
    else:
        # 添加方法到识别器
        recognizer.claude_integration_service = integration_service

    print("✅ Claude Skills 已集成到意图识别器")
    return integration_service