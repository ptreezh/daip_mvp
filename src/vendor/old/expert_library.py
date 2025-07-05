"""智能专家库系统
支持从角色目录递归加载专家信息，自动转换TXT到JSON格式
"""

import dataclasses
import fnmatch
import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class Expert:
    """专家信息数据类"""

    id: str
    name: str
    title: str
    category: str
    specialties: list[str]
    description: str
    experience_years: int
    reputation_score: float
    contact_info: dict[str, str]
    skills: list[str]
    languages: list[str]
    availability: str
    hourly_rate: Optional[float]
    location: str
    education: list[str]
    certifications: list[str]
    projects: list[str]
    bio: str
    source_file: str
    created_at: str
    updated_at: str
    aliases: list[str] = dataclasses.field(default_factory=list)
    tags: list[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式，类型安全，所有 str/int/float 字段都不会为 None"""
        d = asdict(self)
        # 类型安全处理
        str_fields = [
            "id",
            "name",
            "title",
            "category",
            "description",
            "bio",
            "availability",
            "location",
            "source_file",
            "created_at",
            "updated_at",
        ]
        for k in str_fields:
            if k in d and (d[k] is None or not isinstance(d[k], str)):
                d[k] = str(d[k]) if d[k] is not None else ""
        if "experience_years" in d and (
            d["experience_years"] is None or not isinstance(d["experience_years"], int)
        ):
            d["experience_years"] = (
                int(d["experience_years"]) if d["experience_years"] is not None else 0
            )
        if "reputation_score" in d and (
            d["reputation_score"] is None
            or not isinstance(d["reputation_score"], float)
        ):
            d["reputation_score"] = (
                float(d["reputation_score"])
                if d["reputation_score"] is not None
                else 0.0
            )
        if "hourly_rate" in d and (
            d["hourly_rate"] is None or not isinstance(d["hourly_rate"], float)
        ):
            d["hourly_rate"] = (
                float(d["hourly_rate"]) if d["hourly_rate"] is not None else 0.0
            )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Expert":
        """从字典创建专家对象，自动忽略未知字段"""
        # 自动补全所有Expert字段的默认值
        defaults = {
            "id": "",
            "name": "",
            "title": "",
            "category": "",
            "specialties": [],
            "description": "",
            "experience_years": 0,
            "reputation_score": 0.0,
            "contact_info": {},
            "skills": [],
            "languages": [],
            "availability": "",
            "hourly_rate": None,
            "location": "",
            "education": [],
            "certifications": [],
            "projects": [],
            "bio": "",
            "source_file": "",
            "created_at": "",
            "updated_at": "",
            "aliases": [],
            "tags": [],
            "expertise_level": "",
            "prompt_template": "",
        }
        for k, v in defaults.items():
            if k not in data or data[k] is None:
                data[k] = v
        if "aliases" not in data or not data["aliases"]:
            aliases = set()
            if "name" in data and data.get("name"):
                aliases.add(data["name"])
            if "title" in data and data.get("title"):
                aliases.add(data["title"])
            if "tags" in data and data.get("tags"):
                aliases.update(data["tags"])
            if "接待员" in aliases or "高情商接待员" in aliases:
                aliases.add("小暖")
                aliases.add("接待员")
                aliases.add("高情商接待员")
                aliases.add("Receptionist")
            data["aliases"] = list(aliases)
        # 类型安全处理
        for k, v in data.items():
            if v is None:
                if k in [
                    "id",
                    "name",
                    "title",
                    "category",
                    "description",
                    "bio",
                    "availability",
                    "location",
                    "source_file",
                    "created_at",
                    "updated_at",
                ]:
                    data[k] = ""
                elif k in [
                    "specialties",
                    "skills",
                    "languages",
                    "education",
                    "certifications",
                    "projects",
                    "aliases",
                    "tags",
                ]:
                    data[k] = []
                elif k in ["contact_info"]:
                    data[k] = {}
                elif k in ["experience_years"]:
                    data[k] = 0
                elif k in ["reputation_score", "hourly_rate"]:
                    data[k] = 0.0
        # 再次确保所有str/int字段非None
        str_fields = [
            "id",
            "name",
            "title",
            "category",
            "description",
            "bio",
            "availability",
            "location",
            "source_file",
            "created_at",
            "updated_at",
        ]
        for k in str_fields:
            if k in data and (data[k] is None or not isinstance(data[k], str)):
                data[k] = str(data[k]) if data[k] is not None else ""
        if "experience_years" in data and (
            data["experience_years"] is None
            or not isinstance(data["experience_years"], int)
        ):
            data["experience_years"] = (
                int(data["experience_years"])
                if data["experience_years"] is not None
                else 0
            )
        if "reputation_score" in data and (
            data["reputation_score"] is None
            or not isinstance(data["reputation_score"], float)
        ):
            data["reputation_score"] = (
                float(data["reputation_score"])
                if data["reputation_score"] is not None
                else 0.0
            )
        if "hourly_rate" in data and (
            data["hourly_rate"] is None or not isinstance(data["hourly_rate"], float)
        ):
            data["hourly_rate"] = (
                float(data["hourly_rate"]) if data["hourly_rate"] is not None else 0.0
            )
        # 只保留Expert类支持的字段，忽略多余字段
        expert_fields = {f.name for f in dataclasses.fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in expert_fields}
        return cls(**filtered_data)


class ExpertLibrary:
    """专家库管理系统"""

    def __init__(self, roles_directory: str = "roles", auto_load: bool = True):
        self.roles_directory = Path(roles_directory)
        self.experts: dict[str, Expert] = {}
        self.categories: dict[str, list[str]] = {}
        self.search_index: dict[str, list[str]] = {}
        self.conversion_log: list[dict[str, Any]] = []

        # 加载排除配置
        self.exclusion_config = self._load_exclusion_config()

        # 确保角色目录存在
        self.roles_directory.mkdir(exist_ok=True)

        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # 自动加载专家数据
        if auto_load and self.roles_directory.exists():
            try:
                self.load_experts_from_directory()
            except Exception as e:
                self.logger.warning(f"自动加载专家失败: {e}")

    def _load_exclusion_config(self) -> dict[str, Any]:
        """加载排除配置文件"""
        config_path = Path("config/expert_library_config.json")
        default_config = {
            "excluded_files": ["user_defined_roles.json"],
            "excluded_directories": ["user_defined"],
            "excluded_patterns": ["*_batch.json", "*_collection.json"],
        }

        try:
            if config_path.exists():
                with open(config_path, encoding="utf-8") as f:
                    return json.load(f)
            else:
                # 如果配置文件不存在，创建默认配置
                config_path.parent.mkdir(exist_ok=True)
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
                return default_config
        except Exception as e:
            self.logger.warning(f"加载排除配置失败: {e}，使用默认配置")
            return default_config

    def load_experts_from_directory(self, force_reload: bool = False) -> dict[str, Any]:
        """从角色目录递归加载所有专家"""
        self.logger.info(f"开始从目录加载专家: {self.roles_directory}")

        stats = {
            "total_files": 0,
            "txt_files": 0,
            "json_files": 0,
            "converted_files": 0,
            "loaded_experts": 0,
            "errors": [],
        }

        # 需要排除的数组格式文件
        excluded_files = {"user_defined_roles.json"}  # 用户自定义角色集合文件

        # 递归遍历所有文件（包括子目录）
        for file_path in self._recursive_file_search(self.roles_directory):
            stats["total_files"] += 1
            try:
                if file_path.suffix.lower() == ".txt":
                    stats["txt_files"] += 1
                    # 处理TXT文件
                    expert = self._process_txt_file(file_path, force_reload)
                    if expert:
                        self._add_expert(expert)
                        stats["loaded_experts"] += 1
                        if self._was_converted(file_path):
                            stats["converted_files"] += 1
                elif file_path.suffix.lower() == ".json":
                    stats["json_files"] += 1
                    # 处理JSON文件
                    expert = self._process_json_file(file_path)
                    if expert:
                        self._add_expert(expert)
                        stats["loaded_experts"] += 1
            except Exception as e:
                error_msg = f"处理文件 {file_path} 时出错: {e!s}"
                self.logger.error(error_msg)
                stats["errors"].append(error_msg)
        # 构建 role_id 到 expert 的索引
        self.role_id_index = {e.id: e for e in self.experts.values()}
        # 构建搜索索引
        self._build_search_index()
        self.logger.info(f"专家加载完成: {stats}")
        return stats

    def _recursive_file_search(self, directory: Path) -> list[Path]:
        """递归搜索所有角色文件"""
        files = []

        try:
            for item in directory.iterdir():
                if item.is_file() and item.suffix.lower() in [".txt", ".json"]:
                    # 检查是否应该排除此文件
                    if self._should_exclude_file(item):
                        self.logger.info(f"排除文件: {item}")
                        continue
                    files.append(item)
                elif item.is_dir():
                    # 检查是否应该排除此目录
                    if self._should_exclude_directory(item):
                        self.logger.info(f"排除目录: {item}")
                        continue
                    # 递归搜索子目录
                    files.extend(self._recursive_file_search(item))
        except PermissionError:
            self.logger.warning(f"无权限访问目录: {directory}")

        return files

    def _should_exclude_file(self, file_path: Path) -> bool:
        """检查文件是否应该被排除"""
        filename = file_path.name

        # 检查文件名是否在排除列表中
        if filename in self.exclusion_config.get("excluded_files", []):
            return True

        # 检查文件名是否匹配排除模式
        for pattern in self.exclusion_config.get("excluded_patterns", []):
            if fnmatch.fnmatch(filename, pattern):
                return True

        return False

    def _should_exclude_directory(self, dir_path: Path) -> bool:
        """检查目录是否应该被排除"""
        dirname = dir_path.name
        # 只排除配置中明确要求排除的目录（不再默认排除user_defined）
        if dirname in self.exclusion_config.get("excluded_directories", []):
            # 只排除非user_defined目录
            if dirname != "user_defined":
                return True
        return False

    def _process_txt_file(
        self,
        file_path: Path,
        force_reload: bool = False,
    ) -> Optional[Expert]:
        """处理TXT格式的角色文件"""
        try:
            # 检查是否已有对应的JSON文件
            json_path = file_path.with_suffix(".json")

            if json_path.exists() and not force_reload:
                # 如果JSON文件存在且不强制重载，直接加载JSON
                return self._process_json_file(json_path)

            # 读取TXT文件内容
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # 解析TXT内容
            expert_data = self._parse_txt_content(content, file_path)

            if expert_data:
                # 创建专家对象
                expert = Expert(**expert_data)

                # 保存为JSON格式
                self._save_expert_as_json(expert, json_path)

                # 记录转换日志
                self._log_conversion(file_path, json_path, "success")

                return expert

        except Exception as e:
            self.logger.error(f"处理TXT文件 {file_path} 失败: {e}")
            self._log_conversion(file_path, None, "error", str(e))

        return None

    def _parse_txt_content(
        self,
        content: str,
        file_path: Path,
    ) -> Optional[dict[str, Any]]:
        """解析TXT文件内容"""
        lines = content.strip().split("\n")

        # 基础信息
        expert_data = {
            "id": self._generate_expert_id(file_path),
            "name": "",
            "title": "",
            "category": self._extract_category_from_path(file_path),
            "specialties": [],
            "description": "",
            "experience_years": 0,
            "reputation_score": 80.0,  # 默认声誉分数
            "contact_info": {},
            "skills": [],
            "languages": ["中文"],  # 默认语言
            "availability": "可用",
            "hourly_rate": None,
            "location": "",
            "education": [],
            "certifications": [],
            "projects": [],
            "bio": "",
            "source_file": str(file_path),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        current_section = None
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测段落标题
            if self._is_section_header(line):
                # 保存上一个段落的内容
                if current_section and current_content:
                    self._apply_section_content(
                        expert_data,
                        current_section,
                        current_content,
                    )

                current_section = self._normalize_section_name(line)
                current_content = []
            else:
                current_content.append(line)

        # 处理最后一个段落
        if current_section and current_content:
            self._apply_section_content(expert_data, current_section, current_content)

        # 如果没有明确的段落结构，尝试智能解析
        if not expert_data["name"]:
            expert_data = self._smart_parse_unstructured_content(content, expert_data)

        # 验证必要字段
        if not expert_data["name"]:
            expert_data["name"] = file_path.stem

        return expert_data

    def _is_section_header(self, line: str) -> bool:
        """判断是否为段落标题"""
        # 常见的段落标题模式
        section_patterns = [
            r"^#+\s*(.+)",  # Markdown标题
            r"^(.+):$",  # 冒号结尾
            r"^\[(.+)\]$",  # 方括号
            r"^【(.+)】$",  # 中文方括号
            r"^##\s*(.+)",  # 双井号
            r"^-+\s*(.+)\s*-+$",  # 横线包围
        ]

        for pattern in section_patterns:
            if re.match(pattern, line):
                return True

        # 检查是否为常见段落标题
        common_headers = [
            "姓名",
            "名称",
            "专业",
            "技能",
            "经验",
            "教育",
            "项目",
            "联系方式",
            "简介",
            "描述",
            "背景",
            "专长",
            "能力",
            "资质",
            "证书",
            "语言",
            "name",
            "title",
            "skills",
            "experience",
            "education",
            "projects",
            "contact",
            "bio",
            "description",
            "specialties",
            "expertise",
        ]

        for header in common_headers:
            if header in line.lower():
                return True

        return False

    def _normalize_section_name(self, line: str) -> str:
        """标准化段落名称"""
        # 移除标记符号
        clean_line = re.sub(r"^[#\[\]【】\-:：]+\s*", "", line)
        clean_line = re.sub(r"\s*[#\[\]【】\-:：]+$", "", clean_line)

        # 映射到标准字段名
        field_mapping = {
            "姓名": "name",
            "名称": "name",
            "name": "name",
            "职位": "title",
            "职称": "title",
            "title": "title",
            "专业": "specialties",
            "专长": "specialties",
            "specialties": "specialties",
            "技能": "skills",
            "能力": "skills",
            "skills": "skills",
            "经验": "experience",
            "工作经验": "experience",
            "experience": "experience",
            "教育": "education",
            "学历": "education",
            "education": "education",
            "项目": "projects",
            "项目经验": "projects",
            "projects": "projects",
            "联系方式": "contact",
            "联系": "contact",
            "contact": "contact",
            "简介": "bio",
            "个人简介": "bio",
            "bio": "bio",
            "描述": "description",
            "description": "description",
            "语言": "languages",
            "languages": "languages",
            "位置": "location",
            "地点": "location",
            "location": "location",
            "证书": "certifications",
            "资质": "certifications",
            "certifications": "certifications",
        }

        return field_mapping.get(clean_line.lower(), clean_line.lower())

    def _apply_section_content(
        self,
        expert_data: dict[str, Any],
        section: str,
        content: list[str],
    ):
        """应用段落内容到专家数据"""
        content_text = "\n".join(content).strip()

        if section == "name":
            expert_data["name"] = content[0] if content else ""
        elif section == "title":
            expert_data["title"] = content[0] if content else ""
        elif section in ["specialties", "专业", "专长"]:
            expert_data["specialties"] = self._parse_list_content(content)
        elif section in ["skills", "技能", "能力"]:
            expert_data["skills"] = self._parse_list_content(content)
        elif section in ["education", "教育", "学历"]:
            expert_data["education"] = self._parse_list_content(content)
        elif section in ["projects", "项目"]:
            expert_data["projects"] = self._parse_list_content(content)
        elif section in ["languages", "语言"]:
            expert_data["languages"] = self._parse_list_content(content)
        elif section in ["certifications", "证书", "资质"]:
            expert_data["certifications"] = self._parse_list_content(content)
        elif section in ["bio", "简介", "个人简介"]:
            expert_data["bio"] = content_text
        elif section in ["description", "描述"]:
            expert_data["description"] = content_text
        elif section in ["contact", "联系方式", "联系"]:
            expert_data["contact_info"] = self._parse_contact_info(content)
        elif section in ["experience", "经验", "工作经验"]:
            # 尝试提取经验年数
            years = self._extract_experience_years(content_text)
            if years:
                expert_data["experience_years"] = years
        elif section in ["location", "位置", "地点"]:
            expert_data["location"] = content[0] if content else ""

    def _parse_list_content(self, content: list[str]) -> list[str]:
        """解析列表内容"""
        items = []
        for line in content:
            # 处理不同的列表格式
            if line.startswith(("-", "•", "*", "+")):
                items.append(line[1:].strip())
            elif "," in line:
                items.extend([item.strip() for item in line.split(",")])
            elif "，" in line:
                items.extend([item.strip() for item in line.split("，")])
            elif "、" in line:
                items.extend([item.strip() for item in line.split("、")])
            else:
                items.append(line.strip())

        return [item for item in items if item]

    def _parse_contact_info(self, content: list[str]) -> dict[str, str]:
        """解析联系信息"""
        contact_info = {}

        for line in content:
            # 邮箱
            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", line)
            if email_match:
                contact_info["email"] = email_match.group()

            # 电话
            phone_match = re.search(r"[\d\-\+\(\)\s]{10,}", line)
            if phone_match:
                contact_info["phone"] = phone_match.group().strip()

            # 微信
            if "微信" in line or "wechat" in line.lower():
                wechat_match = re.search(r"[:：]\s*(\w+)", line)
                if wechat_match:
                    contact_info["wechat"] = wechat_match.group(1)

        return contact_info

    def _extract_experience_years(self, text: str) -> Optional[int]:
        """提取经验年数"""
        # 匹配年数模式
        patterns = [
            r"(\d+)\s*年",
            r"(\d+)\s*years?",
            r"(\d+)\s*yr",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def _smart_parse_unstructured_content(
        self,
        content: str,
        expert_data: dict[str, Any],
    ) -> dict[str, Any]:
        """智能解析无结构内容"""
        lines = content.strip().split("\n")

        # 第一行通常是姓名
        if lines and not expert_data["name"]:
            expert_data["name"] = lines[0].strip()

        # 查找邮箱和电话
        for line in lines:
            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", line)
            if email_match:
                expert_data["contact_info"]["email"] = email_match.group()

            phone_match = re.search(r"[\d\-\+\(\)\s]{10,}", line)
            if phone_match:
                expert_data["contact_info"]["phone"] = phone_match.group().strip()

        # 将剩余内容作为描述
        if len(lines) > 1:
            expert_data["description"] = "\n".join(lines[1:]).strip()

        return expert_data

    def _generate_expert_id(self, file_path: Path) -> str:
        """生成专家ID"""
        # 基于文件路径生成唯一ID
        path_str = str(file_path.relative_to(self.roles_directory))
        return hashlib.md5(path_str.encode()).hexdigest()[:16]

    def _extract_category_from_path(self, file_path: Path) -> str:
        """从文件路径提取分类"""
        # 使用父目录名作为分类
        relative_path = file_path.relative_to(self.roles_directory)
        if len(relative_path.parts) > 1:
            return relative_path.parts[0]
        return "通用"

    def _process_json_file(self, file_path: Path) -> Optional[Expert]:
        """处理JSON格式的角色文件"""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # 处理数组格式的JSON文件（如user_defined_roles.json）
            if isinstance(data, list):
                # 如果是数组，跳过处理，因为这是批量数据
                self.logger.info(f"跳过数组格式的JSON文件: {file_path}")
                return None

            # 提取 role_id 字段（如果存在）
            role_id = data.get("role_id")

            # 只保留 Expert 类定义的字段，自动过滤多余字段
            valid_fields = {f.name for f in dataclasses.fields(Expert)}
            data = {k: v for k, v in data.items() if k in valid_fields}

            # 确保必要字段存在
            if "id" not in data:
                data["id"] = self._generate_expert_id(file_path)
            if "source_file" not in data:
                data["source_file"] = str(file_path)
            if "created_at" not in data:
                data["created_at"] = datetime.now().isoformat()
            if "updated_at" not in data:
                data["updated_at"] = datetime.now().isoformat()

            expert = Expert.from_dict(data)

            # 将 role_id 作为属性添加到 expert 对象
            if role_id:
                expert.role_id = role_id

            return expert

        except Exception as e:
            self.logger.error(f"处理JSON文件 {file_path} 失败: {e}")

        return None

    def _save_expert_as_json(self, expert: Expert, json_path: Path):
        """保存专家信息为JSON格式"""
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(expert.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.info(f"已保存JSON文件: {json_path}")
        except Exception as e:
            self.logger.error(f"保存JSON文件失败 {json_path}: {e}")

    def _add_expert(self, expert: Expert):
        """添加专家到库中"""
        self.experts[expert.id] = expert

        # 更新分类索引
        if expert.category not in self.categories:
            self.categories[expert.category] = []
        self.categories[expert.category].append(expert.id)

    def _build_search_index(self):
        """构建搜索索引"""
        self.search_index = {}
        self.role_id_index = {}  # 添加 role_id 索引

        for expert_id, expert in self.experts.items():
            # 构建 role_id 索引
            role_id = getattr(expert, "role_id", None)
            if role_id:
                self.role_id_index[role_id] = expert

            # 收集所有可搜索的文本
            searchable_text = [
                expert.name,
                expert.title,
                expert.description,
                expert.bio,
                expert.category,
                expert.location,
            ]
            searchable_text.extend(expert.specialties)
            searchable_text.extend(expert.skills)
            searchable_text.extend(expert.languages)
            searchable_text.extend(expert.education)
            searchable_text.extend(expert.certifications)

            # 提取关键词
            for text in searchable_text:
                if text:
                    words = re.findall(r"\w+", text.lower())
                    for word in words:
                        if len(word) > 1:  # 过滤单字符
                            if word not in self.search_index:
                                self.search_index[word] = []
                            if expert_id not in self.search_index[word]:
                                self.search_index[word].append(expert_id)

    def _was_converted(self, txt_path: Path) -> bool:
        """检查文件是否被转换"""
        return any(
            log["source_file"] == str(txt_path) and log["status"] == "success"
            for log in self.conversion_log
        )

    def _log_conversion(
        self,
        source_path: Path,
        target_path: Optional[Path],
        status: str,
        error: str = None,
    ):
        """记录转换日志"""
        log_entry = {
            "source_file": str(source_path) if source_path is not None else "",
            "target_file": str(target_path) if target_path is not None else "",
            "status": status if status is not None else "",
            "timestamp": datetime.now().isoformat(),
            "error": error if error is not None else "",
        }
        self.conversion_log.append(log_entry)

    def search_experts(
        self,
        query: str,
        category: str = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """搜索专家，支持别名和模糊匹配"""
        if not query.strip():
            return self.get_all_experts(category, limit)
        query_lower = query.lower()
        candidates = []
        for expert in self.experts.values():
            names = [expert.name, expert.title] + getattr(expert, "aliases", [])
            # 精确匹配
            if any(query_lower == (n or "").lower() for n in names):
                candidates.append((expert, 2))
                continue
            # 模糊匹配
            if any(query_lower in (n or "").lower() for n in names):
                candidates.append((expert, 1))
        # 按匹配度和声誉分数排序
        candidates.sort(key=lambda x: (x[1], x[0].reputation_score), reverse=True)
        results = []
        for expert, _ in candidates[:limit]:
            if category is None or expert.category == category:
                expert_dict = expert.to_dict()
                expert_dict["search_score"] = _
                results.append(expert_dict)
        return results

    def get_all_experts(
        self,
        category: str = None,
        limit: int = None,
    ) -> list[dict[str, Any]]:
        """获取所有专家"""
        experts = []

        for expert in self.experts.values():
            if category is None or (
                expert.category == category if expert.category is not None else False
            ):
                experts.append(expert.to_dict())

        # 按声誉分数排序
        experts.sort(key=lambda x: x["reputation_score"], reverse=True)

        if limit:
            experts = experts[:limit]

        return experts

    def get_expert_by_id(self, expert_id: str) -> Optional[dict[str, Any]]:
        """根据ID或别名获取专家，优先 role_id 字段"""
        # 优先 role_id 精确查找
        if hasattr(self, "role_id_index") and expert_id in self.role_id_index:
            return self.role_id_index[expert_id].to_dict()
        expert = self.experts.get(expert_id)
        if expert:
            return expert.to_dict()
        # 支持用name/title/alias查找
        expert_id_lower = expert_id.lower() if expert_id is not None else ""
        for e in self.experts.values():
            names = [e.name, e.title] + getattr(e, "aliases", [])
            if any(expert_id_lower == (n or "").lower() for n in names):
                return e.to_dict()
        # 模糊匹配
        for e in self.experts.values():
            names = [e.name, e.title] + getattr(e, "aliases", [])
            if any(expert_id_lower in (n or "").lower() for n in names):
                return e.to_dict()
        return None

    def get_categories(self) -> dict[str, int]:
        """获取所有分类及专家数量"""
        category_counts = {}
        for category, expert_ids in self.categories.items():
            category_counts[category] = len(expert_ids)
        return category_counts

    def get_experts_by_category(self, category: str) -> list[dict[str, Any]]:
        """根据分类获取专家"""
        if category not in self.categories:
            return []

        experts = []
        for expert_id in self.categories[category]:
            expert = self.experts.get(expert_id)
            if expert:
                experts.append(expert.to_dict())

        return experts

    def get_experts_by_skills(self, skills: list[str]) -> list[dict[str, Any]]:
        """根据技能搜索专家"""
        matching_experts = []

        for expert in self.experts.values():
            expert_skills = [
                skill.lower() for skill in expert.skills if skill is not None
            ]
            expert_specialties = [
                spec.lower() for spec in expert.specialties if spec is not None
            ]

            match_count = 0
            for skill in skills:
                skill_lower = skill.lower() if skill is not None else ""
                if (
                    skill_lower in expert_skills
                    or skill_lower in expert_specialties
                    or any(skill_lower in es for es in expert_skills)
                    or any(skill_lower in es for es in expert_specialties)
                ):
                    match_count += 1

            if match_count > 0:
                expert_dict = expert.to_dict()
                expert_dict["skill_match_count"] = match_count
                expert_dict["skill_match_ratio"] = (
                    match_count / len(skills) if len(skills) > 0 else 0.0
                )
                matching_experts.append(expert_dict)

        # 按匹配度排序
        matching_experts.sort(
            key=lambda x: (x["skill_match_ratio"], x["reputation_score"]),
            reverse=True,
        )

        return matching_experts

    def update_expert(self, expert_id: str, updates: dict[str, Any]) -> bool:
        """更新专家信息"""
        if expert_id not in self.experts:
            return False

        expert = self.experts[expert_id]

        # 更新字段
        for field, value in updates.items():
            if hasattr(expert, field):
                setattr(expert, field, value)

        # 更新时间戳
        expert.updated_at = datetime.now().isoformat()

        # 重新保存JSON文件
        source_file = Path(expert.source_file)
        if source_file.suffix.lower() == ".txt":
            json_file = source_file.with_suffix(".json")
        else:
            json_file = source_file

        self._save_expert_as_json(expert, json_file)

        # 重建搜索索引
        self._build_search_index()

        return True

    def delete_expert(self, expert_id: str) -> bool:
        """删除专家"""
        if expert_id not in self.experts:
            return False

        expert = self.experts[expert_id]

        # 从分类中移除
        if expert.category in self.categories:
            if expert_id in self.categories[expert.category]:
                self.categories[expert.category].remove(expert_id)

        # 从专家库中移除
        del self.experts[expert_id]

        # 重建搜索索引
        self._build_search_index()

        return True

    def add_expert_manually(self, expert_data: dict[str, Any]) -> str:
        """手动添加专家"""
        # 生成ID
        if "id" not in expert_data:
            expert_data["id"] = hashlib.md5(
                f"{expert_data.get('name', '')}{datetime.now().isoformat()}".encode(),
            ).hexdigest()[:16]

        # 设置默认值
        defaults = {
            "title": "",
            "category": "通用",
            "specialties": [],
            "description": "",
            "experience_years": 0,
            "reputation_score": 80.0,
            "contact_info": {},
            "skills": [],
            "languages": ["中文"],
            "availability": "可用",
            "hourly_rate": None,
            "location": "",
            "education": [],
            "certifications": [],
            "projects": [],
            "bio": "",
            "source_file": "manual_entry",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        for key, default_value in defaults.items():
            if key not in expert_data:
                expert_data[key] = default_value

        # 创建专家对象
        expert = Expert.from_dict(expert_data)

        # 添加到库中
        self._add_expert(expert)

        # 保存为JSON文件
        json_path = self.roles_directory / "manual" / f"{expert.id}.json"
        json_path.parent.mkdir(exist_ok=True)
        self._save_expert_as_json(expert, json_path)

        # 重建搜索索引
        self._build_search_index()

        return expert.id

    def get_statistics(self) -> dict[str, Any]:
        """获取统计信息"""
        total_experts = len(self.experts)

        # 分类统计
        category_stats = self.get_categories()

        # 技能统计
        all_skills = []
        for expert in self.experts.values():
            all_skills.extend(expert.skills)
            all_skills.extend(expert.specialties)

        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # 经验统计
        experience_levels = {
            "新手(0-2年)": 0,
            "中级(3-5年)": 0,
            "高级(6-10年)": 0,
            "专家(10年以上)": 0,
        }
        for expert in self.experts.values():
            years = expert.experience_years
            if years <= 2:
                experience_levels["新手(0-2年)"] += 1
            elif years <= 5:
                experience_levels["中级(3-5年)"] += 1
            elif years <= 10:
                experience_levels["高级(6-10年)"] += 1
            else:
                experience_levels["专家(10年以上)"] += 1

        # 声誉分布
        reputation_ranges = {
            "优秀(90+)": 0,
            "良好(80-89)": 0,
            "一般(70-79)": 0,
            "待提升(<70)": 0,
        }
        for expert in self.experts.values():
            score = expert.reputation_score
            if score >= 90:
                reputation_ranges["优秀(90+)"] += 1
            elif score >= 80:
                reputation_ranges["良好(80-89)"] += 1
            elif score >= 70:
                reputation_ranges["一般(70-79)"] += 1
            else:
                reputation_ranges["待提升(<70)"] += 1

        return {
            "total_experts": total_experts,
            "categories": category_stats,
            "top_skills": top_skills,
            "experience_distribution": experience_levels,
            "reputation_distribution": reputation_ranges,
            "conversion_stats": {
                "total_conversions": len(
                    [log for log in self.conversion_log if log["status"] == "success"],
                ),
                "failed_conversions": len(
                    [log for log in self.conversion_log if log["status"] == "error"],
                ),
                "last_update": max(
                    [expert.updated_at for expert in self.experts.values()],
                )
                if self.experts
                else "",
            },
        }

    def export_experts(self, format: str = "json", category: str = None) -> str:
        """导出专家数据"""
        experts = self.get_all_experts(category)

        if format.lower() == "json":
            return json.dumps(experts, ensure_ascii=False, indent=2)
        elif format.lower() == "csv":
            import csv
            import io

            output = io.StringIO()
            if experts:
                fieldnames = experts[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for expert in experts:
                    # 处理列表字段
                    row = expert.copy()
                    for key, value in row.items():
                        if isinstance(value, list):
                            row[key] = "; ".join(str(v) for v in value)
                        elif isinstance(value, dict):
                            row[key] = json.dumps(value, ensure_ascii=False)
                    writer.writerow(row)

            return output.getvalue()
        else:
            raise ValueError(f"不支持的导出格式: {format}")

    def get_conversion_log(self) -> list[dict[str, Any]]:
        """获取转换日志"""
        return self.conversion_log.copy()

    def validate_expert_data(
        self,
        expert_data: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """验证专家数据"""
        errors = []

        # 必需字段检查
        required_fields = ["name"]
        for field in required_fields:
            if not expert_data.get(field):
                errors.append(f"缺少必需字段: {field}")

        # 数据类型检查
        if "experience_years" in expert_data:
            try:
                int(expert_data["experience_years"])
            except (ValueError, TypeError):
                errors.append("experience_years 必须是整数")

        if "reputation_score" in expert_data:
            try:
                score = float(expert_data["reputation_score"])
                if not 0 <= score <= 100:
                    errors.append("reputation_score 必须在0-100之间")
            except (ValueError, TypeError):
                errors.append("reputation_score 必须是数字")

        # 列表字段检查
        list_fields = [
            "skills",
            "specialties",
            "languages",
            "education",
            "certifications",
            "projects",
        ]
        for field in list_fields:
            if field in expert_data and not isinstance(expert_data[field], list):
                errors.append(f"{field} 必须是列表格式")

        return len(errors) == 0, errors
