"""真实角色管理器

从roles/目录加载真实角色定义，验证角色JSON文件完整性，
基于角色定义创建认知代理，并提供角色真实性验证功能。
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RoleValidationStatus(Enum):
    """角色验证状态"""

    VALID = "valid"
    INVALID = "invalid"
    INCOMPLETE = "incomplete"
    CORRUPTED = "corrupted"


@dataclass
class RoleValidationResult:
    """角色验证结果"""

    role_id: str
    status: RoleValidationStatus
    confidence_score: float
    validation_timestamp: datetime
    issues: List[str]
    file_hash: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['validation_timestamp'] = self.validation_timestamp.isoformat()
        return data


@dataclass
class RoleMetadata:
    """角色元数据"""

    role_id: str
    name: str
    category: str
    file_path: str
    file_size: int
    file_hash: str
    last_modified: datetime
    validation_result: RoleValidationResult

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['last_modified'] = self.last_modified.isoformat()
        data['validation_result'] = self.validation_result.to_dict()
        return data


@dataclass
class CognitiveDifference:
    """认知差异"""

    dimension: str
    role1_value: Any
    role2_value: Any
    difference_score: float
    description: str


class RealRoleManager:
    """真实角色管理器
    
    负责从真实的JSON文件加载角色定义，验证角色完整性，
    创建认知代理，并提供角色真实性验证功能。
    """

    def __init__(self, roles_directory: str = "roles"):
        """初始化角色管理器
        
        Args:
            roles_directory: 角色定义文件目录

        """
        self.roles_directory = Path(roles_directory)
        self.loaded_roles: Dict[str, Dict[str, Any]] = {}
        self.role_metadata: Dict[str, RoleMetadata] = {}
        self.validation_cache: Dict[str, RoleValidationResult] = {}

        # 必需字段定义
        self.required_fields = {
            "basic": ["name", "id"],
            "recommended": ["description", "category", "specialties", "skills"],
            "optional": ["experience_years", "reputation_score", "languages", "bio"]
        }

        # 加载角色
        self._load_all_roles()

        logger.info(f"RealRoleManager initialized with {len(self.loaded_roles)} roles from {self.roles_directory}")

    def _load_all_roles(self):
        """加载所有角色定义"""
        if not self.roles_directory.exists():
            logger.error(f"Roles directory not found: {self.roles_directory}")
            return

        json_files = list(self.roles_directory.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files in {self.roles_directory}")

        for json_file in json_files:
            try:
                self._load_single_role(json_file)
            except Exception as e:
                logger.error(f"Failed to load role from {json_file}: {e}")

    def _load_single_role(self, file_path: Path):
        """加载单个角色定义"""
        try:
            with open(file_path, encoding='utf-8') as f:
                role_data = json.load(f)

            # 计算文件哈希
            file_hash = self._calculate_file_hash(file_path)

            # 验证角色数据
            validation_result = self._validate_role_data(role_data, file_path)

            # 获取角色ID
            role_id = self._extract_role_id(role_data, file_path)

            # 创建元数据
            file_stat = file_path.stat()
            metadata = RoleMetadata(
                role_id=role_id,
                name=role_data.get("name", "Unknown"),
                category=role_data.get("category", "Unknown"),
                file_path=str(file_path),
                file_size=file_stat.st_size,
                file_hash=file_hash,
                last_modified=datetime.fromtimestamp(file_stat.st_mtime),
                validation_result=validation_result
            )

            # 存储角色数据和元数据
            self.loaded_roles[role_id] = role_data
            self.role_metadata[role_id] = metadata
            self.validation_cache[role_id] = validation_result

            logger.debug(f"Loaded role: {role_id} from {file_path}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading role from {file_path}: {e}")

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        with open(file_path, 'rb') as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()

    def _extract_role_id(self, role_data: Dict[str, Any], file_path: Path) -> str:
        """提取角色ID"""
        # 尝试多种可能的ID字段
        for id_field in ["id", "role_id", "name"]:
            if id_field in role_data and role_data[id_field]:
                return str(role_data[id_field])

        # 如果没有找到ID，使用文件名
        return file_path.stem

    def _validate_role_data(self, role_data: Dict[str, Any], file_path: Path) -> RoleValidationResult:
        """验证角色数据"""
        role_id = self._extract_role_id(role_data, file_path)
        issues = []
        confidence_score = 0.0

        # 检查必需字段
        missing_basic = [field for field in self.required_fields["basic"]
                        if field not in role_data or not role_data[field]]
        if missing_basic:
            issues.append(f"Missing basic fields: {missing_basic}")
        else:
            confidence_score += 40.0

        # 检查推荐字段
        missing_recommended = [field for field in self.required_fields["recommended"]
                              if field not in role_data or not role_data[field]]
        if not missing_recommended:
            confidence_score += 30.0
        elif len(missing_recommended) < len(self.required_fields["recommended"]):
            confidence_score += 15.0
            issues.append(f"Missing recommended fields: {missing_recommended}")

        # 检查数据类型和格式
        type_issues = self._validate_field_types(role_data)
        if not type_issues:
            confidence_score += 20.0
        else:
            issues.extend(type_issues)
            confidence_score += 10.0

        # 检查内容质量
        content_score = self._validate_content_quality(role_data)
        confidence_score += content_score

        # 确定验证状态
        if confidence_score >= 80.0 and not missing_basic:
            status = RoleValidationStatus.VALID
        elif confidence_score >= 60.0 and not missing_basic:
            status = RoleValidationStatus.INCOMPLETE
        elif missing_basic:
            status = RoleValidationStatus.INVALID
        else:
            status = RoleValidationStatus.CORRUPTED

        return RoleValidationResult(
            role_id=role_id,
            status=status,
            confidence_score=confidence_score,
            validation_timestamp=datetime.now(),
            issues=issues,
            file_hash=self._calculate_file_hash(file_path)
        )

    def _validate_field_types(self, role_data: Dict[str, Any]) -> List[str]:
        """验证字段类型"""
        issues = []

        # 字符串字段
        string_fields = ["name", "id", "description", "category", "bio"]
        for field in string_fields:
            if field in role_data and not isinstance(role_data[field], str):
                issues.append(f"Field '{field}' should be string, got {type(role_data[field])}")

        # 列表字段
        list_fields = ["specialties", "skills", "languages", "education", "certifications"]
        for field in list_fields:
            if field in role_data and not isinstance(role_data[field], list):
                issues.append(f"Field '{field}' should be list, got {type(role_data[field])}")

        # 数值字段
        numeric_fields = ["experience_years", "reputation_score", "hourly_rate"]
        for field in numeric_fields:
            if field in role_data and not isinstance(role_data[field], (int, float, type(None))):
                issues.append(f"Field '{field}' should be numeric, got {type(role_data[field])}")

        return issues

    def _validate_content_quality(self, role_data: Dict[str, Any]) -> float:
        """验证内容质量"""
        score = 0.0

        # 检查描述长度和质量
        description = role_data.get("description", "")
        if len(description) > 100:
            score += 5.0
        if len(description) > 500:
            score += 5.0

        # 检查专业领域数量
        specialties = role_data.get("specialties", [])
        if len(specialties) >= 3:
            score += 5.0
        elif len(specialties) >= 1:
            score += 2.5

        return min(score, 10.0)

    def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """获取角色定义
        
        Args:
            role_id: 角色ID
            
        Returns:
            角色定义数据

        """
        return self.loaded_roles.get(role_id)

    def get_all_roles(self) -> Dict[str, Dict[str, Any]]:
        """获取所有角色定义"""
        return self.loaded_roles.copy()

    def get_role_metadata(self, role_id: str) -> Optional[RoleMetadata]:
        """获取角色元数据"""
        return self.role_metadata.get(role_id)

    def get_roles_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """按类别获取角色"""
        return {
            role_id: role_data
            for role_id, role_data in self.loaded_roles.items()
            if role_data.get("category", "").lower() == category.lower()
        }

    def search_roles(self, query: str, fields: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """搜索角色
        
        Args:
            query: 搜索查询
            fields: 搜索字段列表
            
        Returns:
            匹配的角色

        """
        if fields is None:
            fields = ["name", "description", "specialties", "skills", "category"]

        query_lower = query.lower()
        matching_roles = {}

        for role_id, role_data in self.loaded_roles.items():
            for field in fields:
                field_value = role_data.get(field, "")

                # 处理不同类型的字段
                if isinstance(field_value, str):
                    if query_lower in field_value.lower():
                        matching_roles[role_id] = role_data
                        break
                elif isinstance(field_value, list):
                    if any(query_lower in str(item).lower() for item in field_value):
                        matching_roles[role_id] = role_data
                        break

        return matching_roles

    def verify_role_authenticity(self, role_id: str) -> Dict[str, Any]:
        """验证角色真实性
        
        Args:
            role_id: 角色ID
            
        Returns:
            真实性验证结果

        """
        if role_id not in self.loaded_roles:
            return {"verified": False, "error": "Role not found"}

        metadata = self.role_metadata[role_id]
        validation_result = self.validation_cache[role_id]

        # 重新计算文件哈希以验证完整性
        current_hash = self._calculate_file_hash(Path(metadata.file_path))
        hash_matches = current_hash == metadata.file_hash

        return {
            "verified": True,
            "role_id": role_id,
            "file_path": metadata.file_path,
            "file_hash": metadata.file_hash,
            "current_hash": current_hash,
            "hash_matches": hash_matches,
            "validation_status": validation_result.status.value,
            "confidence_score": validation_result.confidence_score,
            "last_modified": metadata.last_modified.isoformat(),
            "file_size": metadata.file_size,
            "issues": validation_result.issues
        }

    def analyze_cognitive_differences(self, role1_id: str, role2_id: str) -> List[CognitiveDifference]:
        """分析角色间的认知差异
        
        Args:
            role1_id: 第一个角色ID
            role2_id: 第二个角色ID
            
        Returns:
            认知差异列表

        """
        role1 = self.loaded_roles.get(role1_id)
        role2 = self.loaded_roles.get(role2_id)

        if not role1 or not role2:
            return []

        differences = []

        # 分析专业领域差异
        specialties1 = set(role1.get("specialties", []))
        specialties2 = set(role2.get("specialties", []))

        if specialties1 or specialties2:
            overlap = len(specialties1.intersection(specialties2))
            total = len(specialties1.union(specialties2))
            difference_score = 1.0 - (overlap / total if total > 0 else 0)

            differences.append(CognitiveDifference(
                dimension="specialties",
                role1_value=list(specialties1),
                role2_value=list(specialties2),
                difference_score=difference_score,
                description=f"专业领域重叠度: {overlap}/{total} ({overlap/total*100:.1f}%)" if total > 0 else "无专业领域信息"
            ))

        # 分析技能差异
        skills1 = set(role1.get("skills", []))
        skills2 = set(role2.get("skills", []))

        if skills1 or skills2:
            overlap = len(skills1.intersection(skills2))
            total = len(skills1.union(skills2))
            difference_score = 1.0 - (overlap / total if total > 0 else 0)

            differences.append(CognitiveDifference(
                dimension="skills",
                role1_value=list(skills1),
                role2_value=list(skills2),
                difference_score=difference_score,
                description=f"技能重叠度: {overlap}/{total} ({overlap/total*100:.1f}%)" if total > 0 else "无技能信息"
            ))

        # 分析经验差异
        exp1 = role1.get("experience_years", 0)
        exp2 = role2.get("experience_years", 0)

        if exp1 or exp2:
            max_exp = max(exp1, exp2, 1)
            difference_score = abs(exp1 - exp2) / max_exp

            differences.append(CognitiveDifference(
                dimension="experience",
                role1_value=exp1,
                role2_value=exp2,
                difference_score=difference_score,
                description=f"经验差异: {abs(exp1 - exp2)} 年"
            ))

        # 分析类别差异
        cat1 = role1.get("category", "")
        cat2 = role2.get("category", "")

        if cat1 or cat2:
            difference_score = 0.0 if cat1.lower() == cat2.lower() else 1.0

            differences.append(CognitiveDifference(
                dimension="category",
                role1_value=cat1,
                role2_value=cat2,
                difference_score=difference_score,
                description="相同类别" if difference_score == 0 else "不同类别"
            ))

        return differences

    def get_role_uniqueness_metrics(self, role_id: str) -> Dict[str, Any]:
        """获取角色唯一性指标
        
        Args:
            role_id: 角色ID
            
        Returns:
            唯一性指标

        """
        if role_id not in self.loaded_roles:
            return {"error": "Role not found"}

        target_role = self.loaded_roles[role_id]

        # 计算与其他角色的相似度
        similarities = []
        for other_id, other_role in self.loaded_roles.items():
            if other_id != role_id:
                similarity = self._calculate_role_similarity(target_role, other_role)
                similarities.append({
                    "role_id": other_id,
                    "role_name": other_role.get("name", "Unknown"),
                    "similarity_score": similarity
                })

        # 排序并获取最相似的角色
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)

        # 计算唯一性分数
        if similarities:
            max_similarity = similarities[0]["similarity_score"]
            uniqueness_score = 1.0 - max_similarity
        else:
            uniqueness_score = 1.0

        return {
            "role_id": role_id,
            "uniqueness_score": uniqueness_score,
            "most_similar_roles": similarities[:5],
            "total_comparisons": len(similarities),
            "uniqueness_level": self._categorize_uniqueness(uniqueness_score)
        }

    def _calculate_role_similarity(self, role1: Dict[str, Any], role2: Dict[str, Any]) -> float:
        """计算角色相似度"""
        similarity_score = 0.0
        total_weight = 0.0

        # 专业领域相似度 (权重: 0.4)
        specialties1 = set(role1.get("specialties", []))
        specialties2 = set(role2.get("specialties", []))
        if specialties1 or specialties2:
            overlap = len(specialties1.intersection(specialties2))
            union = len(specialties1.union(specialties2))
            specialty_sim = overlap / union if union > 0 else 0
            similarity_score += specialty_sim * 0.4
            total_weight += 0.4

        # 技能相似度 (权重: 0.3)
        skills1 = set(role1.get("skills", []))
        skills2 = set(role2.get("skills", []))
        if skills1 or skills2:
            overlap = len(skills1.intersection(skills2))
            union = len(skills1.union(skills2))
            skill_sim = overlap / union if union > 0 else 0
            similarity_score += skill_sim * 0.3
            total_weight += 0.3

        # 类别相似度 (权重: 0.2)
        cat1 = role1.get("category", "").lower()
        cat2 = role2.get("category", "").lower()
        if cat1 or cat2:
            category_sim = 1.0 if cat1 == cat2 else 0.0
            similarity_score += category_sim * 0.2
            total_weight += 0.2

        # 经验相似度 (权重: 0.1)
        exp1 = role1.get("experience_years", 0)
        exp2 = role2.get("experience_years", 0)
        if exp1 or exp2:
            max_exp = max(exp1, exp2, 1)
            exp_sim = 1.0 - (abs(exp1 - exp2) / max_exp)
            similarity_score += exp_sim * 0.1
            total_weight += 0.1

        return similarity_score / total_weight if total_weight > 0 else 0.0

    def _categorize_uniqueness(self, uniqueness_score: float) -> str:
        """分类唯一性水平"""
        if uniqueness_score >= 0.8:
            return "highly_unique"
        elif uniqueness_score >= 0.6:
            return "moderately_unique"
        elif uniqueness_score >= 0.4:
            return "somewhat_similar"
        else:
            return "highly_similar"

    def get_validation_summary(self) -> Dict[str, Any]:
        """获取验证摘要"""
        total_roles = len(self.loaded_roles)

        if total_roles == 0:
            return {"total_roles": 0, "validation_stats": {}}

        status_counts = {}
        confidence_scores = []

        for result in self.validation_cache.values():
            status_counts[result.status.value] = status_counts.get(result.status.value, 0) + 1
            confidence_scores.append(result.confidence_score)

        return {
            "total_roles": total_roles,
            "validation_stats": {
                "status_distribution": status_counts,
                "average_confidence": sum(confidence_scores) / len(confidence_scores),
                "valid_roles": status_counts.get("valid", 0),
                "validation_rate": status_counts.get("valid", 0) / total_roles * 100
            },
            "file_stats": {
                "total_files": len(self.role_metadata),
                "total_size_bytes": sum(meta.file_size for meta in self.role_metadata.values()),
                "unique_categories": len(set(role.get("category", "") for role in self.loaded_roles.values()))
            }
        }

    def export_role_registry(self) -> Dict[str, Any]:
        """导出角色注册表"""
        return {
            "export_timestamp": datetime.now().isoformat(),
            "total_roles": len(self.loaded_roles),
            "roles_metadata": [meta.to_dict() for meta in self.role_metadata.values()],
            "validation_summary": self.get_validation_summary(),
            "directory_info": {
                "path": str(self.roles_directory),
                "exists": self.roles_directory.exists()
            }
        }

    def reload_roles(self) -> Dict[str, Any]:
        """重新加载角色"""
        old_count = len(self.loaded_roles)

        # 清空现有数据
        self.loaded_roles.clear()
        self.role_metadata.clear()
        self.validation_cache.clear()

        # 重新加载
        self._load_all_roles()

        new_count = len(self.loaded_roles)

        return {
            "reload_timestamp": datetime.now().isoformat(),
            "old_count": old_count,
            "new_count": new_count,
            "change": new_count - old_count,
            "validation_summary": self.get_validation_summary()
        }
