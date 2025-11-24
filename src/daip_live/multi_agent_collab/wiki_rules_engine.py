"""
维基规则合规检查引擎
确保多角色协作内容符合百科全书准则
"""
from typing import Dict, List, Tuple
from datetime import datetime


class WikiRulesEngine:
    """
    维基规则引擎
    确保协作内容符合百科全书标准
    """
    
    def __init__(self):
        self.bias_indicators = [
            "显然", "明显", "肯定", "绝对", "当然", "无疑", "绝对是", "当然是",
            "我认为", "我觉得", "在我看来", "据我所知", "个人认为", "明显是",
            "公认", "大家都认为", "所有人都知道", "无可争议", "不容置疑"
        ]

        self.accuracy_concerns = [
            "绝对正确", "完全错误", "百分之百", "零错误", "永远不会", "永远不变",
            "绝对保证", "不容置疑", "无可争议", "完美无缺", "无懈可击",
            "绝对真理", "永恒不变", "始终如此"
        ]

        self.vandalism_patterns = [
            "####", "%%%%", "@@@@", "****", "++++", "----", "====", "____",
            "破坏", "垃圾", "无意义", "乱写", "胡说八道", "瞎扯", "乱七八糟",
            "&&&&", "^^^^", "####", "++++", "----", "====", "::::", ";;;;"
        ]
    
    def check_neutral_point_of_view(self, content: str) -> Tuple[bool, str]:
        """检查中立观点原则"""
        content_lower = content.lower()
        
        bias_matches = [indicator for indicator in self.bias_indicators if indicator in content_lower]

        if bias_matches:
            return False, f"检测到偏向性表述: {', '.join(bias_matches)}"

        return True, "内容符合中立观点原则"

    def check_factual_accuracy(self, content: str) -> Tuple[bool, str]:
        """检查事实准确性"""
        content_lower = content.lower()

        accuracy_issues = [concern for concern in self.accuracy_concerns if concern in content_lower]

        if accuracy_issues:
            return False, f"检测到绝对性表述: {', '.join(accuracy_issues)}"

        return True, "内容准确性检查通过"

    def detect_vandalism(self, content: str) -> Tuple[bool, str]:
        """检测破坏行为"""
        content_lower = content.lower()

        # 检查破坏性模式
        vandalism_matches = [pattern for pattern in self.vandalism_patterns if pattern in content_lower]

        if vandalism_matches:
            return False, f"检测到破坏性内容: {', '.join(vandalism_matches)}"

        # 检查是否有意义字符比例（检查无意义的重复字符）
        meaningful_chars = sum(1 for c in content if c.isalnum() or c in "，。！？：；、""''（）《》【】")
        total_chars = len(content)

        if total_chars > 0 and meaningful_chars / total_chars < 0.3:
            return False, "内容中无意义字符比例过高，可能为破坏行为"

        return True, "未检测到破坏行为"
    
    def validate_references(self, content: str) -> Tuple[bool, str]:
        """验证参考资料"""
        # 简单检查是否包含引用格式
        has_ref_pattern = any(char in content for char in ["[", "]", "参考", "引自", "来源", "据"])
        has_year = any(year in content for year in [str(y) for y in range(1900, 2030)])
        
        if len(content) > 200 and not (has_ref_pattern or has_year):
            return False, "长内容建议包含参考资料或来源引用"
        
        return True, "参考资料检查通过"
    
    def perform_comprehensive_check(self, content: str) -> Dict[str, Tuple[bool, str]]:
        """执行全面规则检查"""
        return {
            "neutral_point_of_view": self.check_neutral_point_of_view(content),
            "factual_accuracy": self.check_factual_accuracy(content),
            "vandalism_detection": self.detect_vandalism(content),
            "reference_validation": self.validate_references(content)
        }


# 更新Wiki协作会话以集成规则引擎
def integrate_rules_engine():
    """将规则引擎集成到Wiki协作会话中"""
    from daip_live.multi_agent_collab.wiki_collaboration_session import WikiCollaborationSession
    
    # 添加规则检查方法到现有类
    def submit_contribution_with_validation(self, contributor: str, section: str, content: str, 
                                           contribution_type: str = "add"):
        """带规则验证的贡献提交"""
        rules_engine = WikiRulesEngine()
        
        # 进行规则检查
        checks = rules_engine.perform_comprehensive_check(content)
        
        issues = []
        for check_name, (passed, message) in checks.items():
            if not passed:
                issues.append(f"{check_name}: {message}")
                print(f"[WIKI RULES] {check_name.upper()} ISSUE: {message}")
        
        # 即使有规则问题也允许提交，但记录问题
        contribution = self._submit_contribution_original(contributor, section, content, contribution_type)
        
        if issues:
            # 创建需要审核的讨论
            review_topic = f"内容审核_{section}_{len(self.contribution_history)}"
            self.start_discussion(
                review_topic,
                "Rules_Engine",
                f"内容提交但存在以下问题: {'; '.join(issues)}"
            )
        
        return contribution
    
    # 保存原始方法
    if not hasattr(WikiCollaborationSession, '_submit_contribution_original'):
        WikiCollaborationSession._submit_contribution_original = WikiCollaborationSession.submit_contribution
        WikiCollaborationSession.submit_contribution = submit_contribution_with_validation