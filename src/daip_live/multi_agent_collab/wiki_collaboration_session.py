"""
Wiki协作会话管理器
实现多角色AI协作编辑维基词条功能
"""
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Contribution:
    """贡献记录"""
    contributor: str
    section: str
    content: str
    timestamp: datetime
    contribution_type: str  # 'add', 'edit', 'review', 'suggest'


class WikiCollaborationSession:
    """
    维基协作会话
    管理多角色AI对同一词条的协作编辑过程
    """
    
    def __init__(self, title: str, initial_content: str = ""):
        self.session_id = str(uuid.uuid4())
        self.title = title
        self.participants: Dict[str, Dict[str, Any]] = {}
        self.content_sections: Dict[str, str] = {"overview": initial_content}
        self.discussion_threads: Dict[str, List[Dict[str, Any]]] = {}
        self.contribution_history: List[Contribution] = []
        self.revision_history: List[Dict] = []
        self.active = True
        self.created_at = datetime.now()
        
    def add_participant(self, role_name: str, role_profile: Dict[str, Any]):
        """添加参与者到协作会话"""
        self.participants[role_name] = role_profile
        print(f"[WIKI COLLAB] 角色 {role_name} 已加入协作会话 '{self.title}'")

    def submit_contribution(self, contributor: str, section: str, content: str,
                           contribution_type: str = "add") -> Contribution:
        """提交内容贡献"""
        if contributor not in self.participants:
            raise ValueError(f"贡献者 {contributor} 未在此协作会话中注册")
            
        contribution = Contribution(
            contributor=contributor,
            section=section,
            content=content,
            timestamp=datetime.now(),
            contribution_type=contribution_type
        )
        
        # 保存贡献历史
        self.contribution_history.append(contribution)

        # 更新内容部分
        if section not in self.content_sections:
            self.content_sections[section] = ""

        if contribution_type == "edit":
            self.content_sections[section] = content
        else:
            self.content_sections[section] += "\\n" + content
        
        # 记录修订
        revision_entry = {
            "revision_id": str(uuid.uuid4()),
            "contributor": contributor,
            "section": section,
            "action": contribution_type,
            "timestamp": datetime.now(),
            "content_preview": content[:100]  # 记录内容预览用于冲突检测
        }
        self.revision_history.append(revision_entry)

        # 检查是否存在潜在冲突：对同一章节的多次贡献
        self._check_for_potential_conflicts(section, content, contributor, contribution_type)

        print(f"[WIKI COLLAB] {contributor} 在 '{section}' 部分提交 {contribution_type} 贡献")

        return contribution

    def submit_contribution_with_validation(self, contributor: str, section: str, content: str,
                                           contribution_type: str = "add") -> Contribution:
        """带规则验证的贡献提交"""
        from .wiki_rules_engine import WikiRulesEngine

        # 进行规则检查
        rules_engine = WikiRulesEngine()
        checks = rules_engine.perform_comprehensive_check(content)

        issues = []
        for check_name, (passed, message) in checks.items():
            if not passed:
                issues.append(f"{check_name}: {message}")
                print(f"[WIKI RULES] {check_name.upper()} ISSUE: {message}")

        # 即使有规则问题也允许提交，但记录问题以便后续处理
        contribution = self.submit_contribution(contributor, section, content, contribution_type)

        # 如果有规则问题，创建审核讨论
        if issues:
            review_topic = f"内容审核_{section}_问题#{len(self.contribution_history)}"
            if review_topic not in self.discussion_threads:
                self.start_discussion(
                    review_topic,
                    "Rules_Monitor",
                    f"内容提交但存在以下问题: {'; '.join(issues[:3])}..."  # 只显示前3个问题
                )

        return contribution

    def _check_for_potential_conflicts(self, section: str, content: str, contributor: str, contribution_type: str):
        """检查潜在的冲突：检测对同一章节的不兼容贡献"""
        if section in self.content_sections and self.content_sections[section]:
            existing_content = self.content_sections[section]

            # 如果是编辑操作或内容与现有内容不同，可能需要处理
            if contribution_type == "edit" or content != existing_content:
                # 检测潜在冲突的关键词
                conflict_indicators = [
                    "但是", "然而", "不过", "相反", "尽管", "虽然", "却", "但", "而",
                    "contrast", "however", "though", "although", "versus", "vs"
                ]

                # 检查新内容和现有内容是否有矛盾表述
                content_to_check = content.lower()
                existing_to_check = existing_content.lower()

                # 检查是否存在冲突信号词或否定表述
                contradiction_detected = False
                contradiction_phrases = [
                    ("是", "不是"), ("存在", "不存在"), ("肯定", "否定"),
                    ("证明", "反驳"), ("支持", "反对"), ("赞成", "反对")
                ]

                for pos_phrase, neg_phrase in contradiction_phrases:
                    if (pos_phrase in content_to_check and neg_phrase in existing_to_check) or \
                       (neg_phrase in content_to_check and pos_phrase in existing_to_check):
                        contradiction_detected = True
                        break

                if contradiction_detected:
                    print(f"[WIKI CONFLICT] 检测到章节 '{section}' 中的内容冲突!")
                    print(f"  之前: {existing_content[:60]}...")
                    print(f"  现在: {content[:60]}...")

                    # 自动创建冲突讨论
                    conflict_topic = f"内容冲突_{section}"
                    if conflict_topic not in self.discussion_threads:
                        self.start_discussion(
                            conflict_topic,
                            "Conflict_Detector",
                            f"检测到关于 '{section}' 章节的内容冲突，需要参与者协商解决"
                        )
                    else:
                        # 向现有冲突讨论添加评论
                        self.add_discussion_comment(
                            conflict_topic,
                            contributor,
                            f"新贡献与现有内容存在冲突：{content[:100]}..."
                        )

    def start_discussion(self, topic: str, initiator: str, initial_comment: str):
        """开始讨论线程"""
        if topic not in self.discussion_threads:
            self.discussion_threads[topic] = []

        self.discussion_threads[topic].append({
            "participant": initiator,
            "comment": initial_comment,
            "timestamp": datetime.now(),
            "resolved": False
        })

        print(f"[WIKI DISCUSSION] 启动讨论主题: '{topic}' 由 {initiator}")

    def add_discussion_comment(self, topic: str, participant: str, comment: str):
        """添加讨论评论"""
        if topic not in self.discussion_threads:
            self.start_discussion(topic, participant, "讨论初始化")

        self.discussion_threads[topic].append({
            "participant": participant,
            "comment": comment,
            "timestamp": datetime.now(),
            "resolved": False
        })

        print(f"[WIKI DISCUSSION] {participant} 在主题 '{topic}' 下发表评论")

    def resolve_discussion(self, topic: str, resolution: str, resolver: str = "System"):
        """解决讨论"""
        if topic in self.discussion_threads:
            for entry in self.discussion_threads[topic]:
                entry["resolved"] = True

            # 添加解决记录
            self.discussion_threads[topic].append({
                "participant": resolver,
                "comment": f"讨论解决: {resolution}",
                "timestamp": datetime.now(),
                "resolved": True,
                "type": "resolution"
            })

            print(f"[WIKI DISCUSSION] 讨论 '{topic}' 已解决: {resolution}")

    def end_session(self):
        """结束协作会话"""
        self.active = False
        end_time = datetime.now()

        result = {
            "session_id": self.session_id,
            "title": self.title,
            "duration": (end_time - self.created_at).total_seconds(),
            "total_contributions": len(self.contribution_history),
            "total_participants": len(self.participants),
            "content_sections_count": len(self.content_sections),
            "discussion_threads_count": len(self.discussion_threads),
            "revision_count": len(self.revision_history),
            "ended_at": end_time
        }

        print(f"[WIKI COLLAB] 协作会话 '{self.title}' 已结束")
        return result
