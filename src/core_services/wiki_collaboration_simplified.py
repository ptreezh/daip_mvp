"""简化版Wiki协作系统的核心组件实现。

基于KISS、YAGNI和SOLID原则设计，提供从用户意图到自动执行的端到端流程。
"""

import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from abc import ABC, abstractmethod
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TaskType(Enum):
    """任务类型枚举"""
    CREATE = "create"
    UPDATE = "update"
    ENHANCE = "enhance"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SimpleTask:
    """简化任务数据类
    
    职责：存储协作任务的核心信息
    """
    id: str  # 任务ID
    user_input: str  # 用户原始输入
    optimized_intent: str  # 优化后的意图
    target_entry: str  # 目标条目
    task_type: str  # 任务类型 (create/update/enhance)
    status: str  # 状态 (pending/processing/completed/failed)
    created_at: datetime  # 创建时间
    completed_at: Optional[datetime] = None  # 完成时间
    
    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典，用于序列化"""
        data = asdict(self)
        # 处理datetime对象的序列化
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimpleTask':
        """从字典创建对象，用于反序列化"""
        # 处理datetime对象的反序列化
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('completed_at'), str):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)


@dataclass
class RoleFeedback:
    """角色反馈数据类
    
    职责：存储AI角色提供的反馈信息
    """
    task_id: str  # 关联任务ID
    role_name: str  # 角色名
    feedback: str  # 反馈内容
    submitted_at: datetime  # 提交时间
    
    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典，用于序列化"""
        data = asdict(self)
        data['submitted_at'] = self.submitted_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RoleFeedback':
        """从字典创建对象，用于反序列化"""
        if isinstance(data.get('submitted_at'), str):
            data['submitted_at'] = datetime.fromisoformat(data['submitted_at'])
        return cls(**data)


@dataclass
class ExecutionRecord:
    """执行记录数据类
    
    职责：存储任务执行的历史记录
    """
    task_id: str  # 关联任务ID
    old_content: str  # 更新前内容
    new_content: str  # 更新后内容
    executed_at: datetime  # 执行时间
    success: bool  # 是否成功
    
    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典，用于序列化"""
        data = asdict(self)
        data['executed_at'] = self.executed_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionRecord':
        """从字典创建对象，用于反序列化"""
        if isinstance(data.get('executed_at'), str):
            data['executed_at'] = datetime.fromisoformat(data['executed_at'])
        return cls(**data)


# 核心组件接口定义 (遵循SOLID原则中的接口隔离和依赖倒置)
class IntentOptimizer(ABC):
    """意图优化器接口
    
    职责：优化用户表达的意图
    """
    
    @abstractmethod
    def optimize(self, user_input: str) -> Dict[str, Any]:
        """优化用户意图
        
        Args:
            user_input (str): 用户原始输入
            
        Returns:
            dict: {
                "target_entry": "目标条目",
                "task_type": "任务类型",
                "optimized_intent": "优化后的意图描述"
            }
        """
        pass


class TaskCoordinator(ABC):
    """任务协调器接口
    
    职责：协调整个协作任务流程
    """
    
    @abstractmethod
    def initiate_task(self, user_input: str) -> str:
        """发起协作任务
        
        Args:
            user_input (str): 用户原始输入
            
        Returns:
            str: 任务ID
        """
        pass
        
    @abstractmethod
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态
        
        Args:
            task_id (str): 任务ID
            
        Returns:
            dict: 任务状态信息
        """
        pass


class RoleCoordinator(ABC):
    """角色协调器接口
    
    职责：管理角色参与
    """
    
    @abstractmethod
    def assign_and_collect(self, task: SimpleTask) -> List[RoleFeedback]:
        """指派角色并收集反馈
        
        Args:
            task (SimpleTask): 任务对象
            
        Returns:
            List[RoleFeedback]: 角色反馈列表
        """
        pass


class Executor(ABC):
    """执行器接口
    
    职责：执行最终的知识更新
    """
    
    @abstractmethod
    def execute(self, task: SimpleTask, feedbacks: List[RoleFeedback]) -> bool:
        """执行任务
        
        Args:
            task (SimpleTask): 任务对象
            feedbacks (List[RoleFeedback]): 角色反馈列表
            
        Returns:
            bool: 是否成功
        """
        pass


# 具体实现
class SimpleIntentOptimizer(IntentOptimizer):
    """简单的意图优化器实现
    
    职责：基于关键词匹配优化用户意图
    """
    
    def __init__(self):
        # 定义关键词映射
        self.create_keywords = ["创建", "新增", "添加", "需要一个", "需要关于", "建立"]
        self.update_keywords = ["更新", "修改", "更改", "修订", "编辑", "调整"]
        self.enhance_keywords = ["完善", "补充", "增加", "添加更多", "缺少", "丰富"]
        
        # 定义常见的Wiki条目名称，用于匹配（扩展到更多领域）
        self.common_entries = [
            # 技术领域
            "机器学习", "深度学习", "人工智能", "自然语言处理", "计算机视觉",
            "量子计算", "区块链", "大数据", "云计算", "物联网",
            "神经网络", "强化学习", "监督学习", "无监督学习", "大语言模型",
            "算法", "数据结构", "操作系统", "计算机网络", "数据库",
            
            # 社会科学领域
            "社会学", "心理学", "经济学", "政治学", "历史学",
            "哲学", "教育学", "法学", "社会心理学", "行为经济学",
            "国际关系", "公共政策", "文化人类学", "社会工作", "传播学",
            
            # 自然科学领域
            "物理学", "化学", "生物学", "数学", "天文学",
            "地质学", "环境科学", "生态学", "生物化学", "分子生物学",
            
            # 医学和健康领域
            "医学", "临床医学", "公共卫生", "营养学", "心理学",
            "精神病学", "药理学", "病理学", "免疫学", "遗传学",
            
            # 商业和管理领域
            "管理学", "市场营销", "财务管理", "战略管理", "人力资源",
            "创业", "商业模式", "供应链管理", "项目管理", "领导力"
        ]
    
    def optimize(self, user_input: str) -> Dict[str, Any]:
        """优化用户意图
        
        Args:
            user_input (str): 用户原始输入
            
        Returns:
            dict: 优化后的意图信息
        """
        logging.info(f"优化用户意图: {user_input}")
        
        # 确定任务类型
        task_type = self._determine_task_type(user_input)
        
        # 提取目标条目
        target_entry = self._extract_target_entry(user_input)
        
        # 生成优化后的意图描述
        optimized_intent = self._generate_optimized_intent(user_input, task_type, target_entry)
        
        result = {
            "target_entry": target_entry,
            "task_type": task_type,
            "optimized_intent": optimized_intent
        }
        
        logging.info(f"意图优化结果: {result}")
        return result
    
    def _determine_task_type(self, user_input: str) -> str:
        """确定任务类型"""
        input_lower = user_input.lower()
        
        # 检查创建关键词
        for keyword in self.create_keywords:
            if keyword in input_lower:
                return TaskType.CREATE.value
        
        # 检查更新关键词
        for keyword in self.update_keywords:
            if keyword in input_lower:
                return TaskType.UPDATE.value
        
        # 检查完善关键词
        for keyword in self.enhance_keywords:
            if keyword in input_lower:
                return TaskType.ENHANCE.value
        
        # 默认为更新
        return TaskType.UPDATE.value
    
    def _extract_target_entry(self, user_input: str) -> str:
        """提取目标条目"""
        input_lower = user_input.lower()
        
        # 检查是否明确提到了条目名称
        for entry in self.common_entries:
            if entry in user_input or entry.lower() in input_lower:
                return entry
        
        # 如果没有找到明确的条目名称，尝试从输入中提取
        # 这里使用一个简单的启发式方法
        words = user_input.split()
        if len(words) > 0:
            # 返回第一个可能的名词（简化处理）
            return words[0]
        
        # 默认返回"未指定"
        return "未指定"
    
    def _generate_optimized_intent(self, user_input: str, task_type: str, target_entry: str) -> str:
        """生成优化后的意图描述"""
        type_descriptions = {
            TaskType.CREATE.value: "创建",
            TaskType.UPDATE.value: "更新",
            TaskType.ENHANCE.value: "完善"
        }
        
        type_desc = type_descriptions.get(task_type, "更新")
        return f"{type_desc}{target_entry}词条"


class SimpleTaskCoordinator(TaskCoordinator):
    """简单的任务协调器实现
    
    职责：协调整个协作任务流程
    """
    
    def __init__(self, intent_optimizer: IntentOptimizer, 
                 role_coordinator: RoleCoordinator,
                 executor: Executor,
                 storage_manager: 'CollaborationStorageManager'):
        self.intent_optimizer = intent_optimizer
        self.role_coordinator = role_coordinator
        self.executor = executor
        self.storage_manager = storage_manager
    
    def initiate_task(self, user_input: str) -> str:
        """发起协作任务
        
        Args:
            user_input (str): 用户原始输入
            
        Returns:
            str: 任务ID
        """
        logging.info(f"发起协作任务: {user_input}")
        
        # 1. 优化用户意图
        intent_result = self.intent_optimizer.optimize(user_input)
        
        # 2. 创建任务对象
        task_id = str(uuid.uuid4())
        task = SimpleTask(
            id=task_id,
            user_input=user_input,
            optimized_intent=intent_result["optimized_intent"],
            target_entry=intent_result["target_entry"],
            task_type=intent_result["task_type"],
            status=TaskStatus.PROCESSING.value,
            created_at=datetime.now()
        )
        
        # 3. 存储任务
        self.storage_manager.save_task(task)
        
        # 4. 通知任务开始
        logging.info(f"任务 {task_id} 已开始处理")
        
        # 5. 指派角色并收集反馈
        try:
            feedbacks = self.role_coordinator.assign_and_collect(task)
            
            # 保存反馈
            for feedback in feedbacks:
                self.storage_manager.save_feedback(feedback)
            
            # 6. 执行更新
            success = self.executor.execute(task, feedbacks)
            
            # 7. 更新任务状态
            task.status = TaskStatus.COMPLETED.value if success else TaskStatus.FAILED.value
            task.completed_at = datetime.now()
            
            # 8. 保存更新后的任务
            self.storage_manager.save_task(task)
            
            # 9. 通知任务完成
            logging.info(f"任务 {task_id} 已完成，结果: {'成功' if success else '失败'}")
            
            return task_id
        except Exception as e:
            logging.error(f"任务 {task_id} 处理失败: {e}")
            task.status = TaskStatus.FAILED.value
            task.completed_at = datetime.now()
            self.storage_manager.save_task(task)
            return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态
        
        Args:
            task_id (str): 任务ID
            
        Returns:
            dict: 任务状态信息
        """
        task = self.storage_manager.load_task(task_id)
        if not task:
            return {"error": "任务未找到"}
        
        return {
            "task_id": task.id,
            "status": task.status,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }


class SimpleRoleCoordinator(RoleCoordinator):
    """简单的角色协调器实现
    
    职责：管理角色参与
    """
    
    def __init__(self, storage_manager: 'CollaborationStorageManager', role_manager=None):
        # 定义角色专业领域映射（默认映射）
        self.role_domains = {
            "AI研究员": ["机器学习", "深度学习", "人工智能", "神经网络", "大语言模型"],
            "NLP专家": ["自然语言处理", "大语言模型", "文本分析"],
            "计算机视觉专家": ["计算机视觉", "图像识别", "目标检测"],
            "数据科学家": ["大数据", "数据分析", "统计学"],
            "量子物理学家": ["量子计算", "量子力学"],
            "区块链专家": ["区块链", "分布式系统", "加密货币"],
            # 添加社会科学和人文科学领域的角色
            "社会学家": ["社会学", "社会结构", "社会变迁", "社会问题"],
            "心理学家": ["心理学", "认知心理学", "行为心理学", "心理治疗"],
            "经济学家": ["经济学", "宏观经济学", "微观经济学", "金融市场"],
            "政治学家": ["政治学", "政治理论", "国际关系", "公共政策"],
            "历史学家": ["历史学", "世界历史", "文化史", "历史事件"],
            "哲学家": ["哲学", "伦理学", "形而上学", "认识论"],
            "教育学家": ["教育学", "教学方法", "教育心理学", "课程设计"],
            "法律专家": ["法学", "民法", "刑法", "国际法"],
            "医学专家": ["医学", "临床医学", "公共卫生", "医学研究"],
            "环境科学家": ["环境科学", "生态学", "环境保护", "气候变化"],
            "生物学家": ["生物学", "分子生物学", "进化论", "生物技术"]
        }
        self.storage_manager = storage_manager
        self.role_manager = role_manager
        
        # 如果提供了角色管理器，尝试从其中获取角色信息
        if self.role_manager:
            self._load_roles_from_manager()
    
    def _load_roles_from_manager(self):
        """从角色管理器加载角色信息"""
        try:
            # 这里应该调用实际的角色管理器API来获取角色信息
            # 为了简化，我们使用模拟数据
            # 在实际实现中，这将从RoleManager获取动态的角色定义
            pass
        except Exception as e:
            logging.warning(f"无法从角色管理器加载角色信息: {e}")
    
    def assign_and_collect(self, task: SimpleTask) -> List[RoleFeedback]:
        """指派角色并收集反馈
        
        Args:
            task (SimpleTask): 任务对象
            
        Returns:
            List[RoleFeedback]: 角色反馈列表
        """
        logging.info(f"为任务 {task.id} 指派角色并收集反馈")
        
        # 1. 根据任务内容指派角色
        assigned_roles = self._assign_roles(task)
        logging.info(f"指派的角色: {assigned_roles}")
        
        # 2. 收集角色反馈
        feedbacks = []
        for role in assigned_roles:
            feedback = self._collect_feedback_from_role(task, role)
            feedbacks.append(feedback)
            # 保存反馈
            self.storage_manager.save_feedback(feedback)
        
        logging.info(f"收集到 {len(feedbacks)} 条反馈")
        return feedbacks
    
    def _assign_roles(self, task: SimpleTask) -> List[str]:
        """根据任务内容指派角色"""
        target_entry = task.target_entry
        assigned_roles = []
        
        # 首先尝试从角色管理器获取匹配的角色
        if self.role_manager:
            assigned_roles = self._get_roles_from_role_manager(target_entry)
        
        # 如果角色管理器不可用或未返回角色，则使用内置映射
        if not assigned_roles:
            # 查找与目标条目匹配的角色
            for role, domains in self.role_domains.items():
                for domain in domains:
                    if domain in target_entry or target_entry in domain:
                        assigned_roles.append(role)
                        break
        
        # 如果没有找到匹配的角色，尝试更广泛的匹配
        if not assigned_roles:
            # 使用关键词匹配来查找相关角色
            assigned_roles = self._find_relevant_roles_by_keywords(target_entry)
        
        # 如果仍然没有找到匹配的角色，指派通用角色
        if not assigned_roles:
            assigned_roles = ["AI研究员", "数据科学家"]
        
        # 限制最多指派3个角色
        return assigned_roles[:3]
    
    def _get_roles_from_role_manager(self, target_entry: str) -> List[str]:
        """从角色管理器获取匹配的角色"""
        try:
            # 这里应该调用实际的角色管理器API来获取匹配的角色
            # 为了简化，我们使用模拟实现
            # 在实际实现中，这将调用RoleManager的API来获取最适合的角色
            
            # 模拟实现：基于条目名称查找匹配的角色
            # 这只是一个示例，实际实现应该更复杂
            if hasattr(self.role_manager, 'get_roles_by_domain'):
                roles = self.role_manager.get_roles_by_domain(target_entry)
                return roles[:3]  # 限制最多3个角色
        except Exception as e:
            logging.warning(f"从角色管理器获取角色时出错: {e}")
        
        return []
    
    def _find_relevant_roles_by_keywords(self, target_entry: str) -> List[str]:
        """通过关键词匹配查找相关角色"""
        relevant_roles = []
        target_keywords = self._extract_keywords(target_entry)
        
        for role, domains in self.role_domains.items():
            role_keywords = []
            for domain in domains:
                role_keywords.extend(self._extract_keywords(domain))
            
            # 计算关键词匹配度
            match_score = self._calculate_keyword_match_score(target_keywords, role_keywords)
            if match_score > 0.3:  # 阈值可根据需要调整
                relevant_roles.append(role)
        
        # 按匹配度排序
        relevant_roles.sort(key=lambda role: self._calculate_role_relevance_score(role, target_entry), reverse=True)
        return relevant_roles
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取文本中的关键词（简化实现）"""
        # 移除常见停用词并分割关键词
        stop_words = {"的", "和", "与", "及", "以及", "或者", "还是", "但是", "然而", "因此", "所以", "为了", "关于", "对于", "通过", "基于", "利用", "采用"}
        words = [word.strip() for word in text.replace("，", " ").replace(",", " ").split() if word.strip()]
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        return keywords
    
    def _calculate_keyword_match_score(self, target_keywords: List[str], role_keywords: List[str]) -> float:
        """计算关键词匹配度"""
        if not target_keywords or not role_keywords:
            return 0.0
        
        # 计算交集
        common_keywords = set(target_keywords) & set(role_keywords)
        # 使用Jaccard相似度
        return len(common_keywords) / len(set(target_keywords) | set(role_keywords))
    
    def _calculate_role_relevance_score(self, role: str, target_entry: str) -> float:
        """计算角色与目标条目的相关性得分"""
        # 这里可以实现更复杂的相关性计算
        # 例如考虑角色的专业深度、历史表现等因素
        # 目前使用简单的关键词匹配得分
        target_keywords = self._extract_keywords(target_entry)
        role_domains = self.role_domains.get(role, [])
        role_keywords = []
        for domain in role_domains:
            role_keywords.extend(self._extract_keywords(domain))
        
        return self._calculate_keyword_match_score(target_keywords, role_keywords)
    
    def _collect_feedback_from_role(self, task: SimpleTask, role: str) -> RoleFeedback:
        """从角色收集反馈（模拟实现）"""
        logging.info(f"从角色 {role} 收集反馈")
        
        # 首先检查是否已经有保存的反馈
        existing_feedbacks = self.storage_manager.load_feedbacks(task.id)
        for feedback in existing_feedbacks:
            if feedback.role_name == role:
                logging.info(f"使用已存在的反馈 for {role}")
                return feedback
        
        # 根据角色和任务类型生成模拟反馈
        feedback_content = self._generate_feedback(task, role)
        
        feedback = RoleFeedback(
            task_id=task.id,
            role_name=role,
            feedback=feedback_content,
            submitted_at=datetime.now()
        )
        
        return feedback
    
    def _generate_feedback(self, task: SimpleTask, role: str) -> str:
        """生成模拟反馈内容"""
        task_type = task.task_type
        target_entry = task.target_entry
        
        # 根据角色和任务类型生成不同的反馈
        feedback_templates = {
            ("AI研究员", TaskType.CREATE.value): f"建议从基础概念开始介绍{target_entry}，包括其定义、发展历程和主要应用领域。",
            ("AI研究员", TaskType.UPDATE.value): f"建议更新{target_entry}词条中的最新研究成果，特别是近一年的重要突破。",
            ("AI研究员", TaskType.ENHANCE.value): f"建议为{target_entry}词条补充实际应用案例和未来发展趋势。",
            ("NLP专家", TaskType.CREATE.value): f"建议在{target_entry}词条中详细说明其在自然语言处理中的应用。",
            ("NLP专家", TaskType.UPDATE.value): f"建议更新{target_entry}词条中关于自然语言处理技术的最新进展。",
            ("NLP专家", TaskType.ENHANCE.value): f"建议为{target_entry}词条补充更多NLP领域的应用实例。",
            ("数据科学家", TaskType.CREATE.value): f"建议在{target_entry}词条中添加相关数据分析方法和工具介绍。",
            ("数据科学家", TaskType.UPDATE.value): f"建议更新{target_entry}词条中的数据分析案例和最佳实践。",
            ("数据科学家", TaskType.ENHANCE.value): f"建议为{target_entry}词条补充数据科学相关的工具和框架。"
        }
        
        # 尝试获取特定模板
        template = feedback_templates.get((role, task_type))
        if template:
            return template
        
        # 默认反馈
        return f"作为{role}，建议对{target_entry}词条进行详细阐述，确保内容准确且具有专业深度。"


class SimpleExecutor(Executor):
    """简单的执行器实现
    
    职责：执行最终的知识更新
    """
    
    def __init__(self, wiki_service, storage_manager: 'CollaborationStorageManager'):
        self.wiki_service = wiki_service
        self.storage_manager = storage_manager
    
    def execute(self, task: SimpleTask, feedbacks: List[RoleFeedback]) -> bool:
        """执行任务
        
        Args:
            task (SimpleTask): 任务对象
            feedbacks (List[RoleFeedback]): 角色反馈列表
            
        Returns:
            bool: 是否成功
        """
        logging.info(f"执行任务 {task.id}")
        
        try:
            # 1. 基于反馈生成更新内容
            new_content = self._generate_content(task, feedbacks)
            
            # 2. 获取当前内容（如果存在）
            old_content = ""
            current_entry = self.wiki_service.get_entry(task.target_entry)
            if current_entry:
                old_content = current_entry.content
            
            # 3. 执行更新
            if task.task_type == TaskType.CREATE.value:
                # 创建新条目
                result = self.wiki_service.create_entry(
                    entry_name=task.target_entry,
                    content=new_content,
                    author_role="智能助手",
                    tags=["自动生成"],
                    category="自动创建"
                )
            else:
                # 更新现有条目
                # 对于更新和增强任务，我们创建一个新的编辑提案
                proposal_id = self.wiki_service.propose_edit(
                    entry_name=task.target_entry,
                    new_content=new_content,
                    author_role="智能助手",
                    change_summary=f"自动更新: {task.optimized_intent}"
                )
                
                # 自动批准提案
                if proposal_id:
                    result = self.wiki_service.approve(task.target_entry, proposal_id)
                else:
                    result = False
            
            # 4. 记录执行历史
            execution_record = ExecutionRecord(
                task_id=task.id,
                old_content=old_content,
                new_content=new_content,
                executed_at=datetime.now(),
                success=result is not None or result is True  # create_entry返回对象，approve返回布尔值
            )
            
            # 5. 保存执行记录
            self.storage_manager.save_execution_record(execution_record)
            
            logging.info(f"任务 {task.id} 执行{'成功' if execution_record.success else '失败'}")
            return execution_record.success
            
        except Exception as e:
            logging.error(f"执行任务 {task.id} 时出错: {e}")
            return False
    
    def _generate_content(self, task: SimpleTask, feedbacks: List[RoleFeedback]) -> str:
        """基于反馈生成更新内容"""
        logging.info(f"为任务 {task.id} 生成内容")
        
        # 获取当前内容（如果存在）
        current_content = ""
        current_entry = self.wiki_service.get_entry(task.target_entry)
        if current_entry:
            current_content = current_entry.content
        
        if task.task_type == TaskType.CREATE.value:
            # 创建新内容
            content_parts = [f"# {task.target_entry}\n\n"]
            content_parts.append("## 概述\n\n")
            
            # 添加角色反馈作为内容主体
            for feedback in feedbacks:
                content_parts.append(f"### {feedback.role_name}的建议\n\n")
                content_parts.append(f"{feedback.feedback}\n\n")
            
            content_parts.append("## 总结\n\n")
            content_parts.append("本词条由AI团队自动生成，如有更新建议，请通过wiki edit命令提出。")
            
            return "".join(content_parts)
        
        elif task.task_type == TaskType.UPDATE.value:
            # 更新内容 - 在现有内容基础上修改
            content_parts = [f"{current_content}\n\n"]
            content_parts.append("---\n\n")
            content_parts.append("## 自动更新\n\n")
            
            for feedback in feedbacks:
                content_parts.append(f"- {feedback.role_name}: {feedback.feedback}\n")
            
            return "".join(content_parts)
        
        else:  # ENHANCE
            # 完善内容 - 在现有内容基础上添加
            content_parts = [f"{current_content}\n\n"]
            
            if not current_content.endswith("\n"):
                content_parts.append("\n")
                
            content_parts.append("## 补充内容\n\n")
            
            for feedback in feedbacks:
                content_parts.append(f"- {feedback.feedback}\n")
            
            return "".join(content_parts)


# 添加存储管理器
class CollaborationStorageManager:
    """协作存储管理器
    
    职责：管理协作任务相关的数据存储
    """
    
    def __init__(self, storage_path: str = "data/wiki_collaboration"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.tasks_path = self.storage_path / "tasks"
        self.feedback_path = self.storage_path / "feedback"
        self.execution_path = self.storage_path / "execution"
        
        # 创建子目录
        self.tasks_path.mkdir(exist_ok=True)
        self.feedback_path.mkdir(exist_ok=True)
        self.execution_path.mkdir(exist_ok=True)
    
    def save_task(self, task: SimpleTask):
        """保存任务"""
        task_file = self.tasks_path / f"task_{task.id}.json"
        try:
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
            logging.info(f"任务已保存到 {task_file}")
        except Exception as e:
            logging.error(f"保存任务失败: {e}")
    
    def load_task(self, task_id: str) -> Optional[SimpleTask]:
        """加载任务"""
        task_file = self.tasks_path / f"task_{task_id}.json"
        if not task_file.exists():
            return None
        
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return SimpleTask.from_dict(data)
        except Exception as e:
            logging.error(f"加载任务失败: {e}")
            return None
    
    def save_feedback(self, feedback: RoleFeedback):
        """保存反馈"""
        feedback_file = self.feedback_path / f"feedback_{feedback.task_id}_{feedback.role_name}.json"
        try:
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback.to_dict(), f, ensure_ascii=False, indent=2)
            logging.info(f"反馈已保存到 {feedback_file}")
        except Exception as e:
            logging.error(f"保存反馈失败: {e}")
    
    def load_feedbacks(self, task_id: str) -> List[RoleFeedback]:
        """加载任务的所有反馈"""
        feedbacks = []
        for feedback_file in self.feedback_path.glob(f"feedback_{task_id}_*.json"):
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                feedbacks.append(RoleFeedback.from_dict(data))
            except Exception as e:
                logging.error(f"加载反馈失败: {e}")
        return feedbacks
    
    def save_execution_record(self, record: ExecutionRecord):
        """保存执行记录"""
        record_file = self.execution_path / f"execution_{record.task_id}.json"
        try:
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(record.to_dict(), f, ensure_ascii=False, indent=2)
            logging.info(f"执行记录已保存到 {record_file}")
        except Exception as e:
            logging.error(f"保存执行记录失败: {e}")
    
    def load_execution_record(self, task_id: str) -> Optional[ExecutionRecord]:
        """加载执行记录"""
        record_file = self.execution_path / f"execution_{task_id}.json"
        if not record_file.exists():
            return None
        
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ExecutionRecord.from_dict(data)
        except Exception as e:
            logging.error(f"加载执行记录失败: {e}")
            return None