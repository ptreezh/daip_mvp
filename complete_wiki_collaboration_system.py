"""
DAIP-LIVE 多角色Wiki协作系统完整实现
实现多模型协同编辑维基词条的系统
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime
import re


class CollaborationAction(Enum):
    """协作行为类型"""
    ADD_CONTENT = "add_content"
    EDIT_CONTENT = "edit_content"
    REVIEW_CONTENT = "review_content"
    RESOLVE_CONFLICT = "resolve_conflict"
    DISCUSS_TOPIC = "discuss_topic"


@dataclass
class Contribution:
    """贡献记录"""
    contributor: str
    content: str
    timestamp: datetime
    section: str
    action: CollaborationAction
    revision_id: str


@dataclass
class DiscussionThread:
    """讨论线索"""
    topic: str
    messages: List[Tuple[str, str, datetime]]  # (contributor, message, timestamp)
    resolved: bool


class WikiCollaborationSession:
    """
    维基协作会话
    多角色/模型对同一词条的协作编辑
    """
    
    def __init__(self, title: str, initial_content: str = ""):
        self.session_id = str(uuid.uuid4())
        self.title = title
        self.participants: Dict[str, Any] = {}  # 参与者信息
        self.revision_history: List[Dict] = []  # 修订历史
        self.contributions: List[Contribution] = []  # 所有贡献
        self.discussion_threads: Dict[str, DiscussionThread] = {}  # 讨论线索
        self.current_content = initial_content
        self.sections: Dict[str, str] = {"overview": initial_content}  # 章节内容
        self.active = True
        self.created_at = datetime.now()
        self.content_lock = asyncio.Lock()  # 内容修改锁
    
    async def add_participant(self, role_name: str, role_info: Any):
        """添加参与者"""
        self.participants[role_name] = role_info
        print(f"[WIKI COLLAB] 角色 {role_name} 加入协作会话 {self.title}")
    
    async def submit_contribution(self, contributor: str, section: str, content: str, action: CollaborationAction):
        """提交贡献"""
        if contributor not in self.participants:
            raise ValueError(f"贡献者 {contributor} 未在此会话中注册")
        
        async with self.content_lock:  # 确保内容修改的线程安全
            contribution = Contribution(
                contributor=contributor,
                content=content,
                timestamp=datetime.now(),
                section=section,
                action=action,
                revision_id=str(uuid.uuid4())
            )
            
            self.contributions.append(contribution)
            
            # 记录修订历史
            revision_entry = {
                "revision_id": contribution.revision_id,
                "contributor": contributor,
                "section": section,
                "action": action.value,
                "content_preview": content[:50],
                "timestamp": contribution.timestamp,
                "previous_content": self.sections.get(section, "")
            }
            self.revision_history.append(revision_entry)
            
            # 根据行为类型处理贡献
            if action == CollaborationAction.ADD_CONTENT:
                await self._add_content(contributor, section, content)
            elif action == CollaborationAction.EDIT_CONTENT:
                await self._edit_content(contributor, section, content)
            elif action == CollaborationAction.REVIEW_CONTENT:
                await self._review_content(contributor, section, content)
            
            print(f"[WIKI COLLAB] {contributor} 对 {section} 执行 {action.value}: {content[:50]}...")
            
            return contribution
    
    async def _add_content(self, contributor: str, section: str, content: str):
        """添加内容"""
        async with self.content_lock:
            if section not in self.sections:
                self.sections[section] = ""
            
            self.sections[section] += "\\n" + content
            self._update_current_content()
    
    async def _edit_content(self, contributor: str, section: str, content: str):
        """编辑内容"""
        async with self.content_lock:
            if section in self.sections:
                self.sections[section] = content
            else:
                self.sections[section] = content
            self._update_current_content()
    
    async def _review_content(self, reviewer: str, section: str, feedback: str):
        """评审内容"""
        discussion_key = f"review_{section}"
        if discussion_key not in self.discussion_threads:
            self.discussion_threads[discussion_key] = DiscussionThread(
                topic=f"Review of {section}",
                messages=[],
                resolved=False
            )
        
        self.discussion_threads[discussion_key].messages.append(
            (reviewer, feedback, datetime.now())
        )
    
    def _update_current_content(self):
        """更新当前内容"""
        content_parts = []
        for section_name, section_content in self.sections.items():
            content_parts.append(f"## {section_name}\\n{section_content}")
        
        self.current_content = "\\n\\n".join(content_parts)
    
    async def resolve_discussion(self, discussion_topic: str, resolution: str):
        """解决讨论"""
        if discussion_topic in self.discussion_threads:
            thread = self.discussion_threads[discussion_topic]
            thread.resolved = True
            # 可以将决议应用到内容中
            print(f"[WIKI COLLAB] 讨论 '{discussion_topic}' 已解决: {resolution}")
    
    async def get_collaboration_status(self):
        """获取协作状态"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "active": self.active,
            "contributors": list(self.participants.keys()),
            "contributions_count": len(self.contributions),
            "sections_count": len(self.sections),
            "discussions_count": len(self.discussion_threads),
            "revision_count": len(self.revision_history),
            "created_at": self.created_at
        }
    
    async def end_session(self):
        """结束会话"""
        self.active = False
        print(f"[WIKI COLLAB] 协作会话 {self.title} 已结束")
        return {
            "session_id": self.session_id,
            "title": self.title,
            "total_contributions": len(self.contributions),
            "participants_count": len(self.participants),
            "final_content": self.current_content,
            "revision_count": len(self.revision_history),
            "discussion_count": len(self.discussion_threads),
            "sections": list(self.sections.keys())
        }


class WikiRulesEngine:
    """
    维基协作规则引擎
    确保协作遵循百科全书准则
    """
    
    @staticmethod
    async def enforce_neutral_point_of_view(content: str) -> Tuple[bool, str]:
        """执行中立观点原则检测"""
        # 简单检测偏向性语言
        bias_indicators = [
            "明显", "肯定", "当然", "显然", "绝对是", "当然是", 
            "我觉得", "我们认为", "个人认为", "据我所知", 
            "毫无疑问", "必须承认", "理所当然"
        ]
        
        found_biases = []
        for indicator in bias_indicators:
            if indicator in content:
                found_biases.append(indicator)
        
        if found_biases:
            return False, f"检测到可能的偏向性语言: {', '.join(found_biases)}"
        
        return True, "内容符合中立观点原则"
    
    @staticmethod
    async def check_factual_accuracy(content: str) -> Tuple[bool, str]:
        """检查事实准确性（简化版）"""
        # 简单检测明显错误的表达
        accuracy_indicators = [
            "绝对正确", "完全错误", "百分之百", "从来不会错", "永远不变", "永不改变"
        ]
        
        issues = []
        for indicator in accuracy_indicators:
            if indicator in content:
                issues.append(f"可能过于绝对: '{indicator}'")
        
        if issues:
            return False, f"检测到可能的准确性问题: {', '.join(issues)}"
        
        return True, "内容准确性检测通过"
    
    @staticmethod
    async def validate_structure(content: str) -> Tuple[bool, str]:
        """验证百科全书结构"""
        # 检查是否有结构
        has_sections = "\\n#" in content or "\\n##" in content or "\\n###" in content
        has_paragraphs = "\\n" in content and len(content) > 50
        
        if not (has_sections or has_paragraphs or len(content) > 100):
            return False, "内容结构可能不够完整，建议分段或分节"
        
        return True, "结构验证通过"
    
    @staticmethod
    async def detect_vandalism(edit: str) -> Tuple[bool, str]:
        """检测破坏行为"""
        vandalism_signs = [
            "破坏", "垃圾", "无意义", "乱写", "胡说八道",
            "####", "%%%%", "@@@@", "****", "%%%%%", "#####", "+++++", "=====", "-----"
        ]
        
        for sign in vandalism_signs:
            if sign in edit:
                return False, f"检测到可能的破坏行为: '{sign}'"
        
        # 检查是否大部分是无意义字符
        if len(edit) > 0:
            meaningful_char_ratio = len([c for c in edit if c.isalnum() or c in "，。！？：；、"]) / len(edit)
            if meaningful_char_ratio < 0.3:
                return False, "内容包含过多无意义字符，可能为破坏"
        
        return True, "未检测到破坏行为"
    
    @staticmethod 
    async def validate_references(content: str) -> Tuple[bool, str]:
        """验证参考资料格式"""
        # 检查是否有参考文献格式的迹象
        ref_patterns = [
            r"参考[\s\S]*\d{4}",    # "参考2023"等
            r"引自[\s\S]*\w+",     # "引自某某"等
            r"\[\d+\]",            # [1] [2] 等引用格式
            r"参见[\s\S]*\w+",     # "参见某某"等
        ]
        
        has_refs = any(re.search(pattern, content) for pattern in ref_patterns)
        
        if not has_refs and len(content) > 300:
            return False, "长内容建议添加参考资料"
        
        return True, "参考资料验证通过"


class WikiCollaborationEngine:
    """
    维基协作引擎
    管理协作编辑流程、版本控制、冲突解决
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, WikiCollaborationSession] = {}
        self.rules_engine = WikiRulesEngine()
        self.lock = asyncio.Lock()  # 会话管理锁
    
    async def start_collaboration(self, title: str, participants: List[str], initial_content: str = "") -> str:
        """启动协作编辑会话"""
        async with self.lock:
            session = WikiCollaborationSession(title, initial_content)
            
            # 添加参与者
            for participant in participants:
                await session.add_participant(participant, {"joined_at": datetime.now()})
            
            self.active_sessions[session.session_id] = session
            print(f"[WIKI ENGINE] 启动协作会话: '{title}' 会话ID: {session.session_id}")
            
            return session.session_id
    
    async def submit_contribution(self, session_id: str, contributor: str, 
                                  action: CollaborationAction, section: str, content: str):
        """处理协作请求"""
        if session_id not in self.active_sessions:
            raise ValueError(f"会话 {session_id} 不存在")
        
        session = self.active_sessions[session_id]
        
        # 在应用贡献前进行规则检查
        checks = [
            self.rules_engine.enforce_neutral_point_of_view(content),
            self.rules_engine.check_factual_accuracy(content),
            self.rules_engine.validate_structure(content),
            self.rules_engine.detect_vandalism(content)
        ]
        
        # 运行所有规则检查
        results = await asyncio.gather(*[check for check in checks])
        
        issues = []
        for is_valid, msg in results:
            if not is_valid:
                issues.append(msg)
        
        if issues:
            # 检查是否只是警告而非阻止提交
            warnings = [issue for issue in issues if "建议" in issue or "参考" in issue]
            violations = [issue for issue in issues if issue not in warnings]
            
            if violations:
                return {"success": False, "message": "；".join(violations), "warnings": warnings}
        
        # 提交贡献
        contribution = await session.submit_contribution(contributor, section, content, action)
        
        return {
            "success": True,
            "message": f"贡献已提交: {action.value}",
            "revision_id": contribution.revision_id,
            "session_status": {
                "contributors_count": len(session.participants),
                "total_contributions": len(session.contributions),
                "active_sections": list(session.sections.keys())
            },
            "warnings": [msg for _, msg in results if "建议" in msg or "参考" in msg]
        }
    
    async def get_session_status(self, session_id: str):
        """获取会话状态"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        return await session.get_collaboration_status()
    
    async def close_session(self, session_id: str):
        """关闭会话"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} does not exist")
        
        session = self.active_sessions[session_id]
        result = await session.end_session()
        
        del self.active_sessions[session_id]
        print(f"[WIKI ENGINE] 会话 {session.title} 已从活动会话中移除")
        
        return result
    
    async def get_active_sessions(self):
        """获取活动会话列表"""
        return {
            session_id: {
                "title": session.title,
                "participants": len(session.participants),
                "contributions": len(session.contributions),
                "active_since": session.created_at
            }
            for session_id, session in self.active_sessions.items()
        }


# 便捷的协作会话创建函数
async def create_wiki_collaboration(title: str, participants: List[str], initial_content: str = ""):
    """
    便捷函数：创建维基协作会话
    """
    engine = WikiCollaborationEngine()
    session_id = await engine.start_collaboration(title, participants, initial_content)
    
    return engine, session_id


async def demo_wiki_collaboration():
    """
    演示wiki协作功能
    """
    print("="*80)
    print("🔧 多角色维基协作系统演示")
    print("="*80)
    
    # 创建协作引擎
    engine = WikiCollaborationEngine()
    
    # 启动协作会话
    session_id = await engine.start_collaboration(
        "人工智能", 
        ["Researcher_Agent", "Technical_Writer", "Fact_Checker", "Content_Editor"]
    )
    
    print(f"\\n✅ 启动协作会话: {session_id}")
    
    # 模拟不同角色的贡献
    contributions = [
        ("Researcher_Agent", "overview", "人工智能是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统和程序。", CollaborationAction.ADD_CONTENT),
        ("Technical_Writer", "applications", "机器学习是AI的重要子领域，专注于通过数据和经验改善计算机程序的性能。", CollaborationAction.ADD_CONTENT),
        ("Fact_Checker", "overview", "根据最新研究，AI系统的准确性已达到95%以上。", CollaborationAction.ADD_CONTENT),
        ("Content_Editor", "history", "人工智能的概念最早在1956年的达特茅斯会议上被提出。", CollaborationAction.ADD_CONTENT),
    ]
    
    for contributor, section, content, action in contributions:
        result = await engine.submit_contribution(session_id, contributor, action, section, content)
        print(f"\\n📝 {contributor} 提交贡献: {result['message']}")
    
    # 获取会话状态
    status = await engine.get_session_status(session_id)
    print(f"\\n📊 会话状态: {status['title']}")
    print(f"   贡献者: {status['contributors']}")
    print(f"   贡献数量: {status['contributions_count']}")
    print(f"   章节数量: {status['sections_count']}")
    
    # 结束会话
    result = await engine.close_session(session_id)
    print(f"\\n🏁 会话结束: {result['title']}")
    print(f"   合计贡献: {result['total_contributions']}")
    print(f"   参与人数: {result['participants_count']}")
    print(f"   最终章节: {result['sections']}")
    

if __name__ == "__main__":
    asyncio.run(demo_wiki_collaboration())