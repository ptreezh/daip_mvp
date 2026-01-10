"""
增强的意图识别器 - 支持置信度循环和工作流切换
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """意图类型枚举"""
    QUESTION = "question"      # 问题类对话
    CHAT = "chat"            # 普通聊天
    WORKFLOW = "workflow"      # 工作流（辩论、论文下载、Wiki等）


@dataclass
class Intent:
    """意图数据类"""
    name: str
    confidence: float
    parameters: Dict[str, Any]
    tool_name: Optional[str] = None
    description: str = ""
    intent_type: IntentType = IntentType.CHAT
    requires_confidence_check: bool = False
    requires_clarification: bool = False
    clarification_needed: Optional[Any] = None


class EnhancedIntentRecognizer:
    """增强的自然语言意图识别器"""

    def __init__(self):
        """初始化增强意图识别器"""
        # 导入澄清服务
        from daip_live.agent_engine.services.clarification_service import ClarificationService
        self.clarification_service = ClarificationService()

        # 导入技能集成服务
        from daip_live.skills.integration import ClaudeSkillsIntegrationService
        self.claude_integration_service = None  # 初始化为None，将在系统启动时赋值

        # 初始化技能管理器引用（将在系统启动时设置）
        self.skill_manager = None

        # 初始化技能匹配缓存
        self._skill_match_cache = {}

        # 导入模型适配管理器
        try:
            from daip_live.skills.model_adapter_manager import ModelAdapterManager
            self.model_adapter_manager = ModelAdapterManager()
        except Exception as e:
            self.model_adapter_manager = None
            print(f"⚠️  Model adapter manager not available: {e}")

        self.intent_patterns = {
            # 复杂任务功能 - 最高优先级
            "complex_task": {
                "patterns": [
                    # 复杂任务关键词
                    r".*(分析|研究|调查|探讨).*方法",
                    r".*(分析|研究|调查|探讨).*技术",
                    r".*(分析|研究|调查|探讨).*原因",
                    r".*(分析|研究|调查|探讨).*机制",
                    r".*(设计|构建|开发|创建).*系统",
                    r".*(设计|构建|开发|创建).*框架",
                    r".*(开发|实现).*模块",
                    r".*(制定|创建|编写).*策略",
                    r".*(评估|比较|分析).*影响",
                    r".*(评估|比较|分析).*优劣",
                    r".*(探索|探讨|分析).*趋势",
                    r".*(分析|研究|探讨).*前景",
                    r".*(创建|实现).*解决方案",
                    r".*(实现|开发).*功能",
                    r".*(构建|建立|创建).*平台",
                    r".*(开发|构建|设计).*架构",
                    r".*(撰写|编写|编写).*报告",
                    r".*(编写|撰写|整理).*方案",
                    r".*(制定|创建|编写).*计划",
                    r".*(建立|构建|设计).*机制",
                    # 一般复杂意图
                    r".*(深入|全面|详细|系统|综合|整体|完整).*分析",
                    r".*(全面|深入|详细|系统).*研究",
                    r".*(综合|系统|全面).*设计",
                    r".*(详细|全面|深入).*实现",
                    r".*(系统|全面|深入).*评估",
                    r".*(全面|详细|深入).*比较",
                    r".*(综合|系统|全面).*探讨",
                    r".*(全面|深入|详细).*调研",
                    r".*(系统|综合|全面).*解决方案",
                    # 多步骤任务
                    r".*(分析|研究).*并.*(设计|实现|开发)",
                    r".*(设计|开发).*并.*(实现|测试|部署)",
                    r".*(研究|分析).*并.*(评估|比较|总结)",
                    r".*(创建|构建).*并.*(测试|部署|优化)",
                    # 明确的复杂请求
                    r".*帮我.*多方面.*分析.*",
                    r".*帮我.*深入.*研究.*",
                    r".*帮我.*系统.*设计.*",
                    r".*帮我.*全面.*评估.*",
                    r".*帮我.*详细.*规划.*",
                    r".*帮我.*制定.*详细.*计划",
                    r".*帮我.*创建.*完整.*解决方案",
                    r".*帮我.*设计.*完整.*系统",
                    r".*帮我.*进行全面.*调研",
                    r".*帮我.*做个.*综合.*比较",
                    # 项目型任务
                    r".*(开发|构建|创建).*项目",
                    r".*实现.*完整.*功能",
                    r".*(创建|构建|开发).*完整.*系统",
                    r".*(设计|开发).*全流程.*功能",
                    # 专业分析
                    r".*进行.*专业.*分析",
                    r".*进行.*深度.*研究",
                    r".*进行.*全面.*调研",
                    r".*进行.*系统.*评估",
                    r".*进行.*综合.*比较",
                    # 复杂咨询
                    r".*(咨询|建议|推荐).*最佳.*实践",
                    r".*(咨询|建议|推荐).*最优.*方案",
                    r".*(咨询|建议|推荐).*完整.*流程",
                    r".*(咨询|建议|推荐).*系统.*方法"
                ],
                "tool": "complex_task",
                "extract_params": self._extract_complex_task_params,
                "description": "复杂任务处理工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },

            # PA助手功能 - 高优先级
            "personal_assistant": {
                "patterns": [
                    r"个人.*助手.*",
                    r"我的.*助手.*",
                    r"PA.*助手.*",
                    r"私人.*助手.*",
                    r"个人.*助理.*",
                    r"PA.*助理.*",
                    r"智能.*助手.*",
                    r"AI.*助手.*",
                    r"开启.*助手.*",
                    r"启动.*助手.*",
                    r"激活.*助手.*",
                    r"个人.*AI.*助手.*",
                    r"智能.*助理.*",
                    r"我的.*AI.*助手.*",
                    r"助手.*请.*",
                    r"助手.*帮.*",
                    r"助手.*分析.*",
                    r"助手.*总结.*",
                    r"助手.*搜索.*",
                    r"助手.*查找.*",
                    r"助手.*处理.*",
                    r"助手.*功能",
                    r"助手.*能力",
                    r".*助手.*功能",
                    r".*助手.*能力",
                    # 包含"助手"且有动作的表达
                    r".*助手.*帮我.*",
                    r".*助手.*请.*",
                    r".*助手.*帮.*"
                ],
                "tool": "personal_assistant",
                "extract_params": self._extract_assistant_params,
                "description": "个人助手工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },

            # 技能执行工作流 - 高优先级
            "execute_skill": {
                "patterns": [
                    # 明确的技能执行意图
                    r".*[运行|执行|使用].*技能",
                    r".*[帮我|请帮我].*[:：]\s*([^。？！]+)$",
                    # 文本处理相关 - 直接提取文本内容
                    r".*[帮助|帮我|请帮我].*分析\s+(.+?)[。？！]*$",
                    r".*[帮助|帮我|请帮我].*处理\s+(.+?)[。？！]*$",
                    r".*[帮助|帮我|请帮我].*搜索\s+(.+?)[。？！]*$",
                    r".*[帮助|帮我|请帮我].*查找\s+(.+?)[。？！]*$",
                    r".*[帮助|帮我|请帮我].*总结\s+(.+?)[。？！]*$",
                    r".*[帮助|帮我|请帮我].*写\s+(.+?)[。？！]*$",
                    # 通用技能请求
                    r".*帮我.*分析.*",
                    r".*帮我.*处理.*",
                    r".*帮我.*搜索.*",
                    r".*帮我.*总结.*",
                    r".*帮我.*生成.*",
                    r".*帮我.*翻译.*",
                    r".*帮我.*整理.*",
                    r".*帮我.*提取.*",
                    r".*请.*分析.*",
                    r".*请.*处理.*",
                    r".*请.*搜索.*",
                    r".*请.*总结.*",
                    r".*请.*生成.*",
                    r".*请.*整理.*",
                    r".*请.*翻译.*",
                    r".*帮我.*一下.*",
                    r".*请你.*",
                    r".*帮我.*个.*",
                    # 专门的技能请求
                    r".*[执行|运行|使用].*技能[:：]\s*(.+?)$",
                    # 自然语言技能请求（重点增强）
                    r".*[运行|执行|使用].*技能",
                    r".*[运行|启动|使用].*文本分析.*技能",
                    # 简单技能请求 - 但排除更具体的搜索意图
                    r".*[帮我|请帮我].*分析.*",
                    r".*[帮我|请帮我].*处理.*",
                    r".*[帮我|请帮我].*搜索.*",
                    r".*[帮我|请帮我].*查找.*",
                    r".*[帮我|请帮我].*总结.*",
                    # 问题形式但实际是技能请求
                    r".*[帮我|请帮我].*[分析|处理|搜索|查找|总结|翻译|写|创建].*",
                    # 特定技能表达
                    r".*[使用|运行|执行].*[text_analysis|text_analyzer|文档分析|内容分析]",
                    r".*[运行|启动|使用].*文本分析.*技能",
                    # 添加对简短"帮我"请求的支持
                    r"帮我$",
                    r"帮我\s*$",
                    r"帮我[一下|帮忙|帮个忙]?$",
                ],
                "tool": "skill",
                "extract_params": self._extract_skill_params,
                "description": "技能执行工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },

            # 知识库搜索 - 高优先级
            "knowledge_search": {
                "patterns": [
                    r"搜索.*知识库.*(.+)",
                    r"在.*知识库.*搜索.*(.+)",
                    r"查找.*知识.*(.+)",
                    r"查询.*知识.*(.+)",
                    r"知识库.*查询.*(.+)",
                    r"本地.*知识.*(.+)",
                    r"我的.*知识.*(.+)",
                    r"in.*knowledge.*(.+)",
                    r"search.*knowledge.*(.+)",
                    r"find.*knowledge.*(.+)",
                    # 更通用的模式
                    r"在.*知识库.*中.*[搜索|查找|查|找].*",
                    r"在.*本地.*[知识|资料].*[搜索|查找|查|找].*",
                    r"知识库.*[搜索|查找|查|找].*",
                    r"本地.*[知识|资料|文档].*",
                    r"我的.*[知识|资料|文档|文件].*",
                    r".*中.*[搜索|查找|查|找].*[本地|我的|个人|自有].*[知识|资料|信息].*",
                    r".*[搜索|查找|查|找].*[本地|我的|个人|自有].*[知识|资料|信息].*",
                    # 简化模式
                    r"知识.*搜索.*",
                    r"知识.*查找.*",
                    r"本地.*搜索.*",
                    r"本地.*查找.*",
                    # 通用查询
                    r".*在.*我.*的.*[资料|知识|文件].*中.*(搜索|查找|找).*(.*)",
                    r".*在我.*[资料|知识|文件].*中.*(搜索|查找|找).*(.*)",
                    # 本地/我的知识相关
                    r"本地.*知识.*",
                    r"我的.*知识.*",
                    r"个人.*知识.*",
                    r"自有.*知识.*",
                    r"本地.*资料.*",
                    r"我的.*资料.*",
                    r"个人.*资料.*",
                    r"自有.*资料.*"
                ],
                "tool": "knowledge",
                "extract_params": self._extract_knowledge_search_params,
                "description": "知识库搜索",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },

            # 查看Wiki词条 - 高优先级（避免与创建意图冲突）
            "view_wiki": {
                "patterns": [
                    # 专门的查看模式 - 最高优先级
                    r"查看.*词条.*(.+)",
                    r"查看.*维基.*(.+)",
                    r"查看.*百科.*(.+)",
                    r"浏览.*词条.*(.+)",
                    r"浏览.*维基.*(.+)",
                    r"浏览.*百科.*(.+)",
                    # 简洁查看模式
                    r"查看.*[:：\s]+(.+)",
                    r"浏览.*[:：\s]+(.+)",
                    # 查看特定主题
                    r"查看\s+(.+?)\s+词条",
                    r"查看\s+(.+?)\s+维基",
                    r"查看\s+(.+?)\s+百科",
                    r"浏览\s+(.+?)\s+词条",
                    r"浏览\s+(.+?)\s+维基",
                    r"浏览\s+(.+?)\s+百科"
                ],
                "tool": "wiki",
                "extract_params": self._extract_view_wiki_params,
                "description": "查看Wiki词条",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },

            # Wiki工作流 - 优先级调整
            "create_wiki": {
                "patterns": [
                    # 精确的Wiki创建模式 - 最高优先级
                    r"wiki.*create.*",
                    r"create.*wiki.*",
                    r"wiki.*页面.*创建",
                    r"创建.*wiki.*页面",
                    # 维基创建模式 - 提高优先级，避免被复杂任务识别器抢夺
                    r"创建.*维基.*",
                    r"新建.*维基.*",
                    r"写.*维基.*",
                    r"编辑.*维基.*",
                    r"做.*个.*维基.*",
                    r"搞.*个.*维基.*",
                    r"弄.*个.*维基.*",
                    r"建.*个.*维基.*",
                    r"做个.*维基.*",
                    r"建个.*维基.*",
                    # 词条创建模式
                    r"创建.*词条.*",
                    r"新建.*词条.*",
                    r"写.*词条.*",
                    r"编辑.*词条.*",
                    r"协同编辑.*词条.*",
                    r"协作编辑.*词条.*",
                    r"创造.*词条.*",
                    r"制作.*词条.*",
                    r"做个.*词条.*",
                    r"建个.*词条.*",
                    # Wiki相关模式
                    r"创建.*wiki.*",
                    r"新建.*wiki.*",
                    r"写.*wiki.*",
                    r"编辑.*wiki.*",
                    r"wiki.*页面.*",
                    r"create.*wiki.*",
                    r"edit.*wiki.*",
                    # 维基百科模式
                    r"创建.*百科.*",
                    r"写个.*百科.*",
                    r"新建.*百科.*",
                    # 页面创建模式
                    r"创建.*页面.*",
                    r"新建.*页面.*",
                    r"写.*页面.*",
                    # 简单维基/百科模式（放在后面，降低优先级以避免冲突）
                    r".*维基.*",
                    r".*百科.*",
                    r".*词条.*"
                ],
                "tool": "wiki",
                "extract_params": self._extract_wiki_params,
                "description": "Wiki创建工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },

            # 论文检索工作流 - 中优先级
            "search_papers": {
                "patterns": [
                    r"搜索.*论文.*",
                    r"查找.*论文.*",
                    r"找.*论文.*",
                    r"找找.*论文.*",
                    r"论文.*搜索.*",
                    r"论文.*查找.*",
                    r"搜索.*学术.*",
                    r"查找.*学术.*",
                    r"学术.*搜索.*",
                    r"学术.*查找.*",
                    r"arxiv.*搜索.*",
                    r"arxiv.*查找.*",
                    r"download.*paper.*",
                    r"search.*paper.*",
                    r"find.*paper.*",
                    r"download.*papers.*",
                    r"search.*papers.*",
                    r"find.*papers.*",
                    r"搜索.*文献.*",
                    r"查找.*文献.*",
                    r"找.*文献.*",
                    r".*(学术|研究|科学|期刊|arxiv|cite|bibliography).*搜索.*",
                    r".*(学术|研究|科学|期刊|arxiv|cite|bibliography).*查找.*",
                    # 添加简短的论文请求模式
                    r"论文\s+.+",      # "论文 人工智能" - 需要具体主题
                    # 知识库搜索模式（更具体）
                    r".*知识库.*搜索.*",
                    r".*知识库.*查找.*",
                    r".*知识.*搜索.*",
                    r".*搜索.*知识.*",
                    r".*查找.*知识.*",
                ],
                "tool": "search_academic_papers",
                "extract_params": self._extract_search_params,
                "description": "学术论文检索工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },

            # 问题类意图 - 中优先级
            "question": {
                "patterns": [
                    r".+\?",                          # 以问号结尾
                    r"什么是",
                    r"如何",
                    r"为什么",
                    r"怎么",
                    r"怎样",
                    r".*吗\?",
                    r".*呢\?",
                    r"能否",
                    r"可否",
                    r"是否",
                    r"你是谁",
                    r"你是什么",
                    r"帮.*写.*",
                    r"怎么做",
                    r"怎么办.*",
                    # 深度思考相关关键词
                    r".*分析.*",
                    r".*解释.*",
                    r".*评估.*",
                    r".*总结.*",
                    r".*评价.*",
                    r".*研究.*",
                    r".*探讨.*",
                    r".*深思.*",
                    r".*仔细.*想想",
                    r".*认真.*考虑",
                    r".*详细.*说明",
                    r".*深入.*讨论",
                    r".*仔细.*分析",
                    r".*审慎.*回答",
                    r".*深刻.*理解",
                    r".*深度.*思考",
                    r".*细致.*处理",
                    r".*全面.*分析",
                    r".*详细.*解析",
                    # 英文深度思考关键词
                    r".*analyze.*",
                    r".*analyze.*",
                    r".*evaluate.*",
                    r".*evaluate.*",
                    r".*summarize.*",
                    r".*summarize.*",
                    r".*explain.*",
                    r".*think.*deeply.*",
                    r".*detailed.*",
                    r".*comprehensive.*",
                    r".*careful.*consideration.*",
                    r".*thorough.*analysis.*"
                ],
                "tool": None,
                "extract_params": self._extract_question_params,
                "description": "问题类对话",
                "intent_type": IntentType.QUESTION,
                "requires_confidence_check": True
            },
            
            # 普通聊天意图 - 直接回答
            "chat": {
                "patterns": [
                    r"你好",
                    r"hi",
                    r"hello",
                    r"谢谢",
                    r"谢谢.*",
                    r"再见",
                    r"拜拜",
                    r"早上好",
                    r"下午好",
                    r"晚上好",
                    r"你好吗",
                    r"怎么样",
                    r"最近.*怎么样",
                    r"最近.*",
                    r"你.*理.*我",      # "你怎么不理我"
                    r"你.*没.*理.*",    # "你没理我"
                    r"刚.*让.*你.*",    # "刚才让你"
                    r"为.*么.*不.*",    # "为什么不"
                    r".*怎么.*不.*",    # "怎么不"
                    r".*随便.*聊聊.*",   # "随便聊聊"
                    r".*随意.*聊天.*",   # "随意聊天"
                    r".*闲.*聊.*",     # "闲聊"
                    r"你.*好.*",       # "你好啊", "你好呀"等
                    r"哈.*哈.*",       # "哈哈", "哈哈哈"等
                    r"嗯.*",          # "嗯", "嗯嗯"等
                    r"哦.*",          # "哦", "哦哦"等
                    r"啊.*",          # "啊", "啊啊"等
                    r".*聊.*天.*",    # "聊天", "聊聊", "聊一下"等
                    r".*谈.*谈.*",    # "谈谈", "谈一谈"等
                    # 一般性对话
                    r"怎么样.*",      # "怎么样啊", "怎么样呢"
                    r"如何.*",        # "如何啊"
                    r"你.*在.*吗",    # "你在吗", "你还在吗"
                    r"你.*在.*",      # "你在做什么", "你在干啥"
                    r"你.*做.*什么.*", # "你在做什么"
                    r"你.*干.*什么.*", # "你在干什么"
                    r".*吗",         # 一般疑问句后缀
                    r"是.*吗",       # "是吗", "是这样吗"
                    r"对.*吧",       # "对吧", "是吧"
                ],
                "tool": None,
                "extract_params": self._extract_chat_params,
                "description": "普通聊天",
                "intent_type": IntentType.CHAT,
                "requires_confidence_check": False
            },


            # 论文检索工作流 - 进入专门流程
            "search_papers": {
                "patterns": [
                    r"搜索.*论文.*",
                    r"查找.*论文.*",
                    r"找.*论文.*",
                    r"找找.*论文.*",
                    r"论文.*搜索.*",
                    r"论文.*查找.*",
                    r"搜索.*学术.*",
                    r"查找.*学术.*",
                    r"学术.*搜索.*",
                    r"学术.*查找.*",
                    r"arxiv.*搜索.*",
                    r"arxiv.*查找.*",
                    r"download.*paper.*",
                    r"search.*paper.*",
                    r"find.*paper.*",
                    r"download.*papers.*",
                    r"search.*papers.*",
                    r"find.*papers.*",
                    r"搜索.*文献.*",
                    r"查找.*文献.*",
                    r"找.*文献.*",
                    r".*(学术|研究|科学|期刊|arxiv|cite|bibliography).*搜索.*",
                    r".*(学术|研究|科学|期刊|arxiv|cite|bibliography).*查找.*",
                    # 添加简短的论文请求模式
                    r"论文\s+.+",      # "论文 人工智能"
                    r"论文\s*$",       # "论文" (空格后可能有内容)
                    # 添加知识库搜索模式
                    r".*知识库.*搜索.*",
                    r".*知识库.*查找.*",
                    r".*知识库.*搜.*",
                    r".*在.*知识库.*搜索.*",
                    r".*在.*知识库.*查找.*",
                    r".*知识.*搜索.*",
                    r".*搜索.*知识.*",
                    r".*查找.*知识.*",
                    # 自然语言知识库查询
                    r"找.*资料.*",
                    r"查.*资料.*",
                    r"搜索.*资料.*",
                    r"查找.*信息.*",
                    r"搜.*信息.*",
                    r"查.*信息.*",
                    r"查.*一下.*",
                    r"找.*一下.*",
                    r"搜.*一下.*",
                    r"帮我.*找.*",
                    r"帮我.*查.*",
                    r"帮我.*搜索.*",
                    r"给我.*查.*",
                    r"给我.*找.*",
                    r"找.*找.*",
                    r"查.*查.*",
                    r"搜索.*内容.*",
                    r"查找.*内容.*",
                    r".*搜索.*",
                    r".*查找.*",
                    r".*找.*"
                ],
                "tool": "search_academic_papers",
                "extract_params": self._extract_search_params,
                "description": "学术论文检索工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            

            # 论文下载工作流
            "download_paper": {
                "patterns": [
                    # 带ID的具体论文下载
                    r"下载.*论文.*(\d{4}\.\d{4,5}(v\d+)?)",
                    r"下载.*arxiv.*(\d{4}\.\d{4,5}(v\d+)?)",
                    r"download.*arxiv.*(\d{4}\.\d{4,5}(v\d+)?)",
                    r"获取.*论文.*(\d{4}\.\d{4,5}(v\d+)?)",
                    r"download.*paper.*(\d{4}\.\d{4,5}(v\d+)?)",

                    # 查看/阅读论文请求
                    r"查看.*论文.*(\d{4}\.\d{4,5}(v\d+)?)",
                    r"阅读.*论文.*(\d{4}\.\d{4,5}(v\d+)?)",
                    r"看.*论文.*(\d{4}\.\d{4,5}(v\d+)?)",

                    # 不带ID的一般论文/文章/文献下载请求 - 这会触发搜索下载流程
                    r"下载.*论文.*关于.*",  # 需要具体主题
                    r"下载.*关于.*的论文.*",
                    r"获取.*关于.*的论文.*",
                    r"下载.*论文.*[\s:：].*",  # 需要冒号或空格后跟内容
                    r"获取.*论文.*[\s:：].*",

                    # 查看/阅读请求 (没有具体ID时需要搜索)
                    r"查看.*论文.*关于.*",
                    r"阅读.*论文.*关于.*",
                    r"看.*论文.*关于.*",

                    # 通用搜索请求，在没有具体ID时
                    r"论文\s+.+",      # "论文 人工智能" 格式 - 需要具体主题
                ],
                "tool": "download_paper",
                "extract_params": self._extract_download_params,
                "description": "论文下载工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },

            # 知识库管理
            "knowledge_sync": {
                "patterns": [
                    r"同步.*知识库",
                    r"更新.*知识库",
                    r"刷新.*知识",
                    r"同步.*本地知识",
                    r"知识库.*同步",
                    r"知识.*刷新",
                    r"scan.*knowledge",
                    r"refresh.*knowledge"
                ],
                "tool": "knowledge",
                "extract_params": self._extract_knowledge_params,
                "description": "知识库同步",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },

            # 知识库搜索

            # 压缩上下文
            "compress_context": {
                "patterns": [
                    r"压缩.*上下文",
                    r"清理.*历史",
                    r"压缩.*对话",
                    r"compress.*context",
                    r"清理.*内存",
                    r"内存.*管理"
                ],
                "tool": "compress",
                "extract_params": self._extract_compress_params,
                "description": "上下文压缩",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            
            # 项目初始化工作流
            "initialize_project": {
                "patterns": [
                    r"初始化.*项目",
                    r"创建.*项目",
                    r"新建.*项目",
                    r"设置.*项目",
                    r"初始化.*环境",
                    r"setup.*project",
                    r"init.*project",
                    r"设置.*环境"
                ],
                "tool": "scaffold",
                "extract_params": self._extract_scaffold_params,
                "description": "项目初始化工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            
            # 查看辩论历史
            "view_debate_history": {
                "patterns": [
                    r"显示.*辩论.*历史",
                    r"查看.*辩论.*历史",
                    r"辩论.*历史",
                    r"show.*debate.*history",
                    r"list.*debates?",
                    r"view.*debates?",
                    r"what.*debates?.*there",
                    r"show.*past.*debates?",
                    r"list.*debate.*sessions?",
                    r"view.*debate.*sessions?",
                    r"辩论.*列表",
                    r"历史.*辩论",
                    r"过去.*辩论.*哪些",
                    r"之前的.*辩论.*情况",
                    r"最近.*辩论.*结果",
                    r"上次.*辩论.*情况",
                    r"近期.*辩论.*记录",
                    r"历史.*记录.*辩论",
                    r"show.*debate.*history"
                ],
                "tool": None,  # 不需要特定工具，通过TUI直接处理
                "extract_params": self._extract_debate_history_params,
                "description": "查看辩论历史",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },
            
            # 查看特定辩论历史
            "view_specific_debate": {
                "patterns": [
                    r"显示.*辩论.*(\w+)",
                    r"查看.*辩论.*(\w+)",
                    r"查看.*辩论.*session.*(\w+)",
                    r"查看.*session.*(\w+).*辩论",
                    r"显示.*debate.*(\w+)",
                    r"view.*debate.*(\w+)",
                    r"show.*debate.*(\w+)",
                    r"view.*session.*(\w+)",
                    r"show.*session.*(\w+)"
                ],
                "tool": None,  # 不需要特定工具，通过TUI直接处理
                "extract_params": self._extract_specific_debate_params,
                "description": "查看特定辩论历史",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            },

            # 辩论工作流
            "start_debate": {
                "patterns": [
                    # 简单辩论请求支持 - 优先级较高
                    r"辩论\s*$",       # "辩论" 单独请求
                    r"辩论\s+(.+)$",   # "辩论 [主题]" 格式

                    # 多模型相关辩论
                    r"多模型辩论\s*$",      # "多模型辩论" 单独请求
                    r"多模型辩论\s+(.+)$",  # "多模型辩论 [主题]" 格式
                    r"多模态辩论\s*$",      # "多模态辩论"
                    r"多模态辩论\s+(.+)$",  # "多模态辩论 [主题]"

                    # 原有经典辩论模式
                    r"开始.*辩论",
                    r"发起.*辩论",
                    r"发起.*一个.*辩论",
                    r"辩论.*话题",
                    r"辩论.*主题",
                    r"辩论[一下吧]",    # 匹配辩论+下/一/吧
                    r"辩论下.*",      # 明确匹配"辩论下"开头
                    r"辩论.*一下",
                    r"辩论.*吧",
                    r"让我.*辩论.*",
                    r"让我.*跟.*辩论",
                    r"跟.*辩论.*",
                    r"开展.*辩论",
                    r"启动.*辩论",
                    r"讨论.*辩题",
                    r"进行.*辩论",
                    r"我们来辩论.*",
                    r"咱们来辩论.*",
                    r"一起来辩论.*",
                    r"我想要辩论.*",
                    r"我想辩论.*",
                    r"让我们辩论.*",
                    r"让我们.*辩论",
                    r"关于.*的辩论",
                    r"就.*展开辩论",
                    r"针对.*辩论",
                    r"围绕.*辩论",
                    r"我们.*辩论.*",    # 匹配"我们辩论 XXX"
                    r"我们要.*辩论.*",   # 匹配"我们要辩论 XXX"
                    r"辩论.*吧.*",      # 匹配"辩论吧，关于XXX"
                    r"debate.*topic",
                    r"discuss.*debate",
                    r"start.*debate",
                    r"begin.*debate",
                    r"let's.*debate",
                    r"let us.*debate"
                ],
                "tool": "debate",
                "extract_params": self._extract_debate_params,
                "description": "辩论工作流",
                "intent_type": IntentType.WORKFLOW,
                "requires_confidence_check": False
            }
        }
    
    def recognize_intent(self, text: str, session_id: str = "default") -> Optional[Intent]:
        """
        识别用户输入的意图

        Args:
            text: 用户输入文本
            session_id: 会话ID用于上下文管理

        Returns:
            识别到的意图，如果没有匹配则返回None
        """
        text = text.strip().lower()

        best_intent = None
        best_confidence = 0.0

        for intent_name, intent_config in self.intent_patterns.items():
            for pattern in intent_config["patterns"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # 计算匹配置信度，对不同类型的意图使用不同的计算方式
                    matched_text = match.group(0)

                    # 对于特定的、包含明确关键词的匹配，给予更高权重
                    if intent_name in ["download_paper", "search_papers"] and len(matched_text) < 3:
                        # 如果是论文相关但匹配的文本太短，降低置信度
                        confidence = len(matched_text) / len(text) * 0.5  # 降低权重
                    elif intent_name == "chat":
                        # 普通聊天意图的置信度计算
                        confidence = len(matched_text) / len(text)
                        # 对特定的聊天模式给予高置信度
                        if any(chat_pattern in text for chat_pattern in ["你好", "hello", "hi", "谢谢", "再见", "拜拜", "嗯", "哦", "啊", "哈"]):
                            confidence = min(confidence * 1.5, 1.0)  # 提高权重
                    else:
                        # 标准的置信度计算
                        confidence = len(matched_text) / len(text)

                    if confidence > best_confidence:
                        # 提取参数
                        params = intent_config["extract_params"](text, match)

                        best_intent = Intent(
                            name=intent_name,
                            confidence=confidence,
                            parameters=params,
                            tool_name=intent_config["tool"],
                            description=intent_config["description"],
                            intent_type=intent_config["intent_type"],
                            requires_confidence_check=intent_config["requires_confidence_check"]
                        )
                        best_confidence = confidence

    def _is_certainly_chat(self, text: str) -> bool:
        """检查文本是否明确是普通聊天"""
        # 检查是否是明确的聊天短语
        chat_indicators = [
            "嗯", "哦", "啊", "嗯嗯", "哦哦", "啊啊", "哈哈", "嘿嘿", "吼吼",
            "嗯?", "哦?", "啊?", "诶", "咦", "噢", "哎", "哎呀", "哎呀呀",
            "嗯嗯嗯", "哦哦哦", "啊啊啊", "嘿嘿嘿", "哈哈哈", "嘻嘻嘻",
            "拜拜", "bye", "88", "晚安", "早安", "午安"
        ]
        return any(indicator in text for indicator in chat_indicators)

    def _is_likely_chat(self, text: str) -> bool:
        """检查文本是否可能是普通聊天"""
        # 检查文本特征
        if len(text) < 5:
            # 短文本更可能是普通聊天
            return True

        # 检查是否包含聊天语气词
        chat_words = ["吗", "呢", "啊", "呀", "吧", "嘛", "了", "哦", "嗯", "哈"]
        if any(word in text for word in chat_words):
            return True

        # 检查是否是疑问句但不包含特定功能词
        if text.endswith("吗") or text.endswith("？") or text.endswith("?"):
            # 排除明确的功能请求
            non_chat_indicators = ["下载", "搜索", "查找", "论文", "维基", "辩论", "创建", "执行"]
            if not any(indicator in text for indicator in non_chat_indicators):
                return True

        return False

    def recognize_intent(self, text: str, session_id: str = "default") -> Optional[Intent]:
        """
        识别用户输入的意图

        Args:
            text: 用户输入文本
            session_id: 会话ID用于上下文管理

        Returns:
            识别到的意图，如果没有匹配则返回None
        """
        text = text.strip().lower()

        # 预处理：检查是否明显是普通聊天
        if self._is_certainly_chat(text):
            return Intent(
                name="chat",
                confidence=0.8,
                parameters={"chat_content": text},
                tool_name=None,
                description="普通聊天",
                intent_type=IntentType.CHAT,
                requires_confidence_check=False
            )

        best_intent = None
        best_confidence = 0.0

        for intent_name, intent_config in self.intent_patterns.items():
            for pattern in intent_config["patterns"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # 计算匹配置信度，对不同类型的意图使用不同的计算方式
                    matched_text = match.group(0)

                    # 对于特定的、包含明确关键词的匹配，给予更高权重
                    if intent_name in ["download_paper", "search_papers"]:
                        # 如果是论文相关，检查匹配文本是否包含实际内容
                        if len(matched_text) < 4:
                            # 如果匹配的文本太短，降低置信度
                            confidence = len(matched_text) / len(text) * 0.3  # 大幅降低权重
                        else:
                            # 否则使用标准计算但增加对具体关键词的权重
                            confidence = len(matched_text) / len(text)
                            # 检查是否包含具体的学术关键词
                            if any(keyword in text for keyword in ["arxiv", "1234.", "v1", "论文", "学术", "期刊", "研究"]):
                                confidence = min(confidence * 1.2, 1.0)
                    elif intent_name == "chat":
                        # 普通聊天意图的置信度计算
                        confidence = len(matched_text) / len(text)
                        # 对特定的聊天模式给予高置信度
                        if any(chat_pattern in text for chat_pattern in ["你好", "hello", "hi", "谢谢", "再见", "拜拜", "嗯", "哦", "啊", "哈"]):
                            confidence = min(confidence * 1.5, 1.0)  # 提高权重
                    else:
                        # 标准的置信度计算
                        confidence = len(matched_text) / len(text)

                        # 对于wiki相关的意图，如果匹配模式非常精确（如"wiki create"），提高置信度
                        if intent_name == "create_wiki":
                            # 检查是否包含明确的wiki create模式
                            if "wiki create" in text or re.search(r"wiki\s+create", text, re.IGNORECASE):
                                confidence = min(confidence * 1.5, 1.0)  # 提高权重

                    if confidence > best_confidence:
                        # 提取参数
                        params = intent_config["extract_params"](text, match)

                        best_intent = Intent(
                            name=intent_name,
                            confidence=confidence,
                            parameters=params,
                            tool_name=intent_config["tool"],
                            description=intent_config["description"],
                            intent_type=intent_config["intent_type"],
                            requires_confidence_check=intent_config["requires_confidence_check"]
                        )
                        best_confidence = confidence

        # 设置置信度阈值
        if best_intent and best_confidence > 0.3:
            # 检查是否需要澄清（缺少关键词或参数）
            self._check_intent_clarification(best_intent, session_id, text)
            return best_intent
        elif best_intent and best_confidence <= 0.3:
            # 如果匹配到意图但置信度较低，检查是否是普通聊天
            # 对于某些模糊的输入，如果无法明确识别意图，返回普通聊天意图
            if best_intent and best_intent.name in ["search_papers", "download_paper"]:
                # 如果匹配的是论文相关但置信度低，更倾向于认为是普通聊天
                if any(chat_word in text for chat_word in ["怎么", "为何", "为什么", "是吗", "对吧", "呢", "啊", "呀", "吧"]):
                    # 认为是普通聊天
                    return Intent(
                        name="chat",
                        confidence=0.4,  # 低于阈值但表明这是一个聊天意图
                        parameters={"chat_content": text},
                        tool_name=None,
                        description="普通聊天",
                        intent_type=IntentType.CHAT,
                        requires_confidence_check=False
                    )

        # 如果没有找到高置信度的意图，但文本看起来像是普通聊天，返回聊天意图
        if not best_intent and self._is_likely_chat(text):
            return Intent(
                name="chat",
                confidence=0.5,
                parameters={"chat_content": text},
                tool_name=None,
                description="普通聊天",
                intent_type=IntentType.CHAT,
                requires_confidence_check=False
            )

        return None

    def _check_intent_clarification(self, intent: Intent, session_id: str, original_text: str):
        """检查意图是否需要澄清，如缺少关键词或参数"""
        # 检查是否缺少关键词
        missing_keywords = self.clarification_service.check_missing_keywords(intent.name, intent.parameters)
        if missing_keywords:
            intent.requires_clarification = True
            intent.clarification_needed = missing_keywords
            return

        # 检查是否缺少参数
        missing_params = self.clarification_service.check_missing_parameters(intent.name, intent.parameters)
        if missing_params:
            intent.requires_clarification = True
            intent.clarification_needed = missing_params
            return

        # 特殊处理：检查维基意图是否缺少标题参数
        if intent.name == "create_wiki":
            title = (intent.parameters.get("title") or "").strip()
            original_clean = original_text.strip() if original_text else ""

            # 检查参数是否确实缺失
            if not title or title == "":
                # 检查是否原始文本只包含通用命令词而没有实际标题
                generic_phrases = ["创建维基", "写个维基", "新建维基", "做个维基", "创建百科", "写个百科", "新建百科", "创建页面", "写个页面", "新建页面"]
                is_generic = any(phrase in original_clean for phrase in generic_phrases)
                if is_generic or len(original_clean.split()) <= 2:
                    # 设置澄清需求
                    intent.requires_clarification = True
                    intent.clarification_needed = {
                        "type": "missing_keywords",
                        "message": "请输入您想创建的维基页面标题，例如：创建维基 人工智能 或 写个维基 量子计算",
                        "required_parameters": ["title"]
                    }
                    return
            elif title == original_clean:
                # 如果标题等于原始文本，说明没有正确提取到标题
                intent.requires_clarification = True
                intent.clarification_needed = {
                    "type": "missing_keywords",
                    "message": "请提供具体的维基页面标题，例如：创建维基 项目计划 或 新建百科 机器学习",
                    "required_parameters": ["title"]
                }
                return

        # 特殊处理：检查论文搜索意图是否缺少查询参数
        elif intent.name == "search_papers":
            query = (intent.parameters.get("query") or "").strip()
            original_clean = original_text.strip() if original_text else ""

            if not query or query == "":
                # 检查是否是通用搜索词汇或短语
                generic_terms = ["搜索", "查找", "找", "查", "资料", "信息", "论文", "内容", "一下", "一点", "点", "东西"]
                generic_phrases = ["搜索论文", "查找论文", "找论文", "查论文", "下载论文", "搜索资料", "查找资料", "找资料"]

                is_generic = any(phrase in original_clean for phrase in generic_phrases) or \
                           any(term in original_clean for term in generic_terms and len(original_clean.split()) <= 2)

                if is_generic:
                    # 确实是通用搜索词，需要澄清
                    intent.requires_clarification = True
                    intent.clarification_needed = {
                        "type": "missing_keywords",
                        "message": "请输入搜索关键词，例如：论文 人工智能 或 搜索 机器学习",
                        "required_parameters": ["query"]
                    }
                    return
                else:
                    # 如果输入有一定长度且不是通用命令词，使用它作为查询
                    if len(original_clean) > 3 and not any(keyword in original_clean for keyword in generic_terms):
                        intent.parameters["query"] = original_clean
                        intent.requires_clarification = False
                        intent.clarification_needed = None
                        return
                    else:
                        # 仍然需要澄清
                        intent.requires_clarification = True
                        intent.clarification_needed = {
                            "type": "missing_keywords",
                            "message": "请输入搜索关键词，例如：论文 人工智能 或 搜索 机器学习",
                            "required_parameters": ["query"]
                        }
                        return
            else:
                # 查询参数存在，不需要澄清
                intent.requires_clarification = False
                intent.clarification_needed = None
                return  # 添加return语句，防止继续执行到默认设置

        # 特殊处理：检查论文下载意图是否缺少参数
        elif intent.name == "download_paper":
            paper_id = intent.parameters.get("paper_id")
            search_query = intent.parameters.get("search_query", "")
            original_clean = original_text.strip() if original_text else ""

            # 如果既没有ID也没有有效的搜索查询，需要澄清
            if not paper_id and (not search_query or search_query == ""):
                # 检查是否只是通用命令词
                generic_phrases = ["下载论文", "获取论文", "下载文章", "获取文章", "下载文献", "获取文献"]

                is_generic = any(phrase in original_clean for phrase in generic_phrases)
                if is_generic or len(original_clean.split()) <= 2:
                    intent.requires_clarification = True
                    intent.clarification_needed = {
                        "type": "missing_keywords",
                        "message": "请提供论文标题、主题或arXiv ID，例如：下载论文 人工智能 或 下载 1234.5678",
                        "required_parameters": ["paper_id or search_query"]
                    }
                    return
            elif not paper_id and search_query and search_query != "":
                # 有搜索词且不为空，不需要澄清，会执行搜索下载流程
                intent.requires_clarification = False
                intent.clarification_needed = None
                return  # 添加return语句，防止继续执行到默认设置
            elif paper_id:
                # 有ID，不需要澄清
                intent.requires_clarification = False
                intent.clarification_needed = None
                return  # 添加return语句，防止继续执行到默认设置
            else:
                # 其他情况：如果没有ID也没有有效搜索查询，标记为需要澄清
                intent.requires_clarification = True
                intent.clarification_needed = {
                    "type": "missing_keywords",
                    "message": "请提供论文ID或搜索关键词",
                    "required_parameters": ["paper_id or search_query"]
                }
                return  # 添加return语句，防止继续执行到默认设置

        # 特殊处理：检查技能执行意图是否缺少参数
        elif intent.name == "execute_skill":
            skill_name = (intent.parameters.get("skill_name") or "").strip()
            query = (intent.parameters.get("query") or "").strip()
            content = (intent.parameters.get("content") or "").strip()
            action = (intent.parameters.get("action") or "").strip()
            original_clean = original_text.strip() if original_text else ""

            # 使用content作为主要参数，如果为空则使用query
            main_content = content if content else query

            if not main_content or main_content == "":
                # 不总是需要澄清 - 检查是否应该使用原始文本作为默认值
                if len(original_clean) > 5:  # 如果原始输入有一定长度
                    # 使用原始文本作为内容参数，除非它只是通用命令词
                    generic_command_words = ["帮我", "执行技能", "运行技能", "使用技能", "开始技能", "启用技能", "启动技能"]
                    if any(keyword in original_clean for keyword in generic_command_words):
                        # 如果输入是通用命令词，仍需要澄清
                        intent.requires_clarification = True
                        intent.clarification_needed = {
                            "type": "missing_keywords",
                            "message": "请提供要处理的内容，例如：帮我分析 这段文本内容",
                            "required_parameters": ["content"]
                        }
                        return
                    else:
                        # 使用原始输入作为内容参数
                        intent.parameters["content"] = original_clean
                        intent.requires_clarification = False
                        intent.clarification_needed = None
                else:
                    # 输入太短，标记需要澄清
                    intent.requires_clarification = True
                    intent.clarification_needed = {
                        "type": "missing_keywords",
                        "message": "请提供具体内容，例如：帮我分析 人工智能发展趋势 或 执行文本分析 这段代码",
                        "required_parameters": ["content"]
                    }
                    return
            else:
                # 内容参数存在，不需要澄清
                intent.requires_clarification = False
                intent.clarification_needed = None
                return  # 添加return语句，防止继续执行到默认设置

        # 特殊处理：检查辩论意图是否缺少参数
        elif intent.name == "start_debate":
            topic = (intent.parameters.get("topic") or "").strip()
            original_clean = original_text.strip() if original_text else ""

            # 检查是否缺少辩论主题
            if not topic or topic == "":
                # 检查是否只包含通用命令词而不包含具体主题
                generic_phrases = [
                    "辩论", "展开辩论", "开始辩论", "发起辩论",
                    "多模型辩论", "多智能体辩论", "多角色辩论",
                    "multi-agent debate", "multi-model debate"
                ]

                is_generic = any(phrase in original_clean.replace(" ", "") for phrase in ["辩论", "展开辩论", "开始辩论", "发起辩论"]) or \
                           any(generic in original_clean for generic in ["多模型辩论", "多智能体辩论", "多角色辩论"])

                if is_generic or len(original_clean) <= 4:
                    intent.requires_clarification = True
                    intent.clarification_needed = {
                        "type": "missing_keywords",
                        "message": "请输入辩论主题，例如：辩论 AI伦理 或 多模型辩论 量子计算",
                        "required_parameters": ["topic"]
                    }
                    return
            elif topic:  # 如果主题存在且不为空
                # 检查主题是否是有效的辩论内容
                if topic == original_clean and len(original_clean) <= 4:
                    # 可能只是命令词，标记需要澄清
                    intent.requires_clarification = True
                    intent.clarification_needed = {
                        "type": "missing_keywords",
                        "message": "请输入具体的辩论主题，例如：辩论 人工智能未来 或 开始辩论 AI伦理",
                        "required_parameters": ["topic"]
                    }
                    return
                else:
                    # 有具体主题，不需要澄清
                    intent.requires_clarification = False
                    intent.clarification_needed = None
                    return

        # 为所有未设置澄清的意图设置默认值
        if not hasattr(intent, 'requires_clarification') or intent.requires_clarification is None:
            intent.requires_clarification = False
            intent.clarification_needed = None

        # 额外检查：某些通用性很强的请求，即使参数存在也可能需要澄清
        # 但只对execute_skill以外的意图应用此规则
        if (original_text.strip() in ["帮我", "帮帮我", "帮我一下", "帮我个忙"] or
            (original_text.strip().startswith("帮我") and len(original_text.strip()) <= 6 and intent.name != "execute_skill")):
            # 如果这是通用帮助请求且没有明确内容，设置为需要澄清
            # 但不覆盖已设置的澄清状态
            pass  # 此规则已在前面的execute_skill处理中应用
    
    def _extract_question_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取问题参数"""
        return {
            "question": text,
            "requires_confidence_check": True
        }
    
    def _extract_chat_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取聊天参数"""
        return {
            "chat_content": text,
            "requires_confidence_check": False
        }
    
    def _extract_search_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取论文搜索参数"""
        # 尝试提取搜索关键词
        keywords = []

        # 常见学术关键词模式
        academic_patterns = [
            r"关于(.+?)的论文",
            r"搜索(.+?)论文",
            r"查找(.+?)相关",
            r"search.*for(.+)",
            r"find.*papers.*about(.+)"
        ]

        for pattern in academic_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                keywords.append(m.group(1).strip())

        # 如果没有找到特定关键词，进一步检查是否只是命令词而没有具体内容
        if not keywords:
            # 移除常见的命令词，看看是否剩下有意义的内容
            cleaned_text = re.sub(r"(搜索|查找|找|search|find|论文|paper|下载|获取|fetch|download)", "", text, flags=re.IGNORECASE)
            # 清理多余的空格
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

            # 需要确保不是通用命令词，且有实际内容
            if cleaned_text and cleaned_text not in ["", "下载", "获取", "获取", "download", "fetch", "资料", "信息", "内容", "东西"] and len(cleaned_text) > 2:
                keywords = [cleaned_text]
            else:
                keywords = [""]  # 没有找到有用的内容

        # 不使用默认关键词，而是返回真实提取的内容或空值
        query = keywords[0] if keywords and len(keywords) > 0 and keywords[0] != "" else ""

        return {
            "query": query,
            "max_results": 5,  # 默认5篇
            "source": "arxiv"  # 默认arxiv源
        }
    
    def _extract_download_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取论文下载参数"""
        import re
        # 首先尝试从正则匹配中提取ID
        paper_id = match.group(1) if match.groups() else None

        # 如果没有从正则中提取到ID，尝试更智能的提取方式
        search_query = None
        if not paper_id:
            # 更精确地查找arXiv ID模式 (4位数字.数字部分，如 1234.56789)
            arxiv_id_match = re.search(r'(\d{4}\.\d{4,5}(v\d+)?)', text)
            if arxiv_id_match:
                paper_id = arxiv_id_match.group(1)

        if not paper_id:
            # 去掉命令词，获取可能的搜索关键词
            command_patterns = [
                r"下载.*论文",
                r"下载.*文章",
                r"下载.*文献",
                r"下载.*资料",
                r"获取.*论文",
                r"获取.*文章",
                r"获取.*文献",
                r"获取.*资料",
                r"查看.*论文",
                r"查看.*文章",
                r"阅读.*论文",
                r"阅读.*文章",
                r"看.*论文",
                r"看.*文章",
                r"论文.*下载",
                r"论文.*获取",
                r"论文.*查看",
                r"论文.*阅读"
            ]

            # 移除命令部分，提取可能的关键词
            clean_text = text
            for pattern in command_patterns:
                clean_text = re.sub(pattern, "", clean_text, flags=re.IGNORECASE).strip()

            # 再次尝试从清理后的文本中提取ID
            if not paper_id:
                arxiv_id_match = re.search(r'(\d{4}\.\d{4,5}(v\d+)?)', clean_text)
                if arxiv_id_match:
                    paper_id = arxiv_id_match.group(1)

            # 如果找到了ID，就不需要搜索查询
            if paper_id:
                search_query = None
            else:
                # 如果没有找到ID，使用清理后的文本作为搜索查询
                if clean_text and len(clean_text.strip()) > 0 and clean_text != text.strip() and len(clean_text.strip()) > 1:
                    search_query = clean_text.strip()
                elif clean_text and len(clean_text.strip()) > 1 and clean_text != "":
                    # 即使clean_text=text.strip()，如果clean_text有实际内容，也使用它（比如"下载论文 机器学习" -> 提取"机器学习"）
                    # 检查是否是"命令 + 空格 + 内容"的格式
                    import re
                    parts_by_cmd = re.split(r'(?:下载|获取)\s*(?:论文|文章|文献|资料)\s*', text, flags=re.IGNORECASE)
                    if len(parts_by_cmd) > 1:
                        # 取最后一个部分作为可能的查询
                        possible_query = parts_by_cmd[-1].strip()
                        if len(possible_query) > 0 and possible_query not in ["", "下载", "获取", "查看", "阅读", "看"]:
                            search_query = possible_query
                        else:
                            # 如果还是没有找到明确内容，使用clean_text
                            search_query = clean_text.strip() if len(clean_text.strip()) > 1 else ""
                    else:
                        search_query = clean_text.strip()  # 使用清理后的文本
                else:
                    # 如果没有明确关键词，尝试从原文本中提取（去除命令词）
                    import re
                    parts = re.split(r'[关于|的|是|关于.*的]', text)
                    if len(parts) > 1:
                        possible_query = parts[-1].strip()  # 取最后一部分作为可能的查询
                        if len(possible_query) > 2:  # 确保不是空或太短
                            search_query = possible_query
                        else:
                            search_query = ""  # 需要澄清
                    else:
                        # 如果还是找不到，标记为需要澄清
                        search_query = ""

        # 如果既有ID又有查询，优先使用ID（更具体）
        if paper_id and search_query:
            search_query = None  # 有具体ID时不需要搜索

        return {
            "paper_id": paper_id,  # 如果有具体ID则使用
            "search_query": search_query,  # 如果没有ID则使用搜索关键词
            "save_path": None,
            "format": "pdf"
        }
    
    def _extract_debate_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取辩论参数"""
        # 尝试提取辩论主题
        topic_patterns = [
            r"辩论.*[:：](.+)",
            r"话题[:：](.+)",
            r"关于(.+?)的辩论",
            r"debate.*about(.+)"
        ]

        topic = None
        for pattern in topic_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                topic = m.group(1).strip()
                break

        # 如果没有找到特定主题，检查是否已经有具体主题（比如"开始辩论 AI伦理"）
        if not topic or topic == text:  # 如果topic等于原始text，说明没有真正提取到主题
            # 使用更智能的方法提取主题
            # 首先检查是否包含"辩论"并尝试从后续内容提取主题
            if "辩论" in text:
                parts = text.split("辩论")
                if len(parts) > 1 and len(parts[1].strip()) > 0:
                    # 看看辩论后的部分是否是具体主题
                    after_debate = parts[1].strip()
                    if after_debate and after_debate not in ["开始", "发起", "我们来", "让我", "让", ""]:
                        topic = after_debate
                    else:
                        topic = ""  # 只是通用命令词
                else:
                    # 如果parts[1]不存在或为空，检查是否文本以"辩论"结尾或只是"辩论"
                    if text.strip() == "辩论" or re.match(r"^\s*辩论\s*$", text):
                        topic = ""  # 简单的"辩论"命令，需要澄清
                    else:
                        # 检查是否是"多模型辩论"这类格式，但没有具体内容
                        plain_debate_patterns = [
                            r"多模型辩论\s*$",
                            r"多模态辩论\s*$",
                            r"多角色辩论\s*$",
                            r"多智能体辩论\s*$",
                            r"^[多|多]*[模型|模态|角色|智能体]*辩论\s*$"  # 匹配各种前缀+辩论
                        ]

                        is_plain_debate = any(re.search(pattern, text, re.IGNORECASE) for pattern in plain_debate_patterns)
                        if is_plain_debate:
                            topic = ""  # 多模型辩论但没有具体内容，需要澄清
                        else:
                            # 尝试其他方式提取，例如检查文本是否有空格分隔
                            words = text.split()
                            debate_word_indices = [i for i, word in enumerate(words) if "辩论" in word]

                            if debate_word_indices:
                                debate_idx = debate_word_indices[0]
                                if debate_idx < len(words) - 1:
                                    # 辩论词后面有内容，提取作为主题
                                    after_debate_words = words[debate_idx + 1:]
                                    if after_debate_words:
                                        topic = " ".join(after_debate_words).strip()
                                    else:
                                        topic = ""  # 没有内容
                                else:
                                    topic = ""  # 只是辩论命令词
                            else:
                                topic = text  # 如果不是通用命令，使用原始文本
            else:
                topic = ""  # 没有找到有用的主题

        return {
            "topic": topic,
            "roles": None,  # 使用默认角色
            "rounds": 3     # 默认3轮
        }
    
    def _extract_view_wiki_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取查看Wiki参数"""
        title = ""

        # 优先使用正则表达式的捕获组
        if match.groups():
            # 获取所有捕获组，使用第一个非空的
            for group in match.groups():
                if group and group.strip():
                    title = group.strip()
                    break

        # 如果正则没有捕获到标题，或捕获不完整，使用智能提取方法
        if not title or len(title) < 2:  # 如果标题太短，可能是提取错误
            # 智能提取标题：处理"查看wiki词条 中美贸易战"、"查看维基 人工智能"这种格式
            # 从原始文本中提取命令词后的所有内容
            command_patterns = [
                r"查看\s*wiki\s*词条\s*(.+)",
                r"查看\s*词条\s*(.+)",
                r"查看\s*维基\s*(.+)",
                r"查看\s*百科\s*(.+)",
                r"浏览\s*词条\s*(.+)",
                r"浏览\s*维基\s*(.+)",
                r"浏览\s*百科\s*(.+)",
                r"查看\s+(.+)",
                r"浏览\s+(.+)"
            ]

            for pattern in command_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m and m.group(1):
                    extracted = m.group(1).strip()
                    # 检查是否是合理的标题（至少2个字符且不包含命令词）
                    if len(extracted) >= 2 and not any(cmd in extracted for cmd in ["查看", "浏览", "词条", "维基", "百科"]):
                        title = extracted
                        break

        # 如果仍然没有提取到标题，尝试更通用的提取方式
        if not title:
            # 移除常见的查看命令词，提取核心标题
            command_words = [
                "查看", "浏览", "view", "show", "display", "get", "read",
                "查看词条", "查看维基", "查看百科", "浏览词条", "浏览维基", "浏览百科"
            ]

            # 按长度排序，优先匹配长命令词
            sorted_commands = sorted(command_words, key=len, reverse=True)

            original_text = text.strip()
            for cmd in sorted_commands:
                if original_text.startswith(cmd):
                    title = original_text[len(cmd):].strip()
                    break
                elif f"{cmd} " in original_text or original_text.startswith(cmd + " "):
                    # 在文本中找到命令词后跟空格，提取其后面的内容
                    pos = original_text.find(cmd + " ")
                    if pos != -1:
                        title = original_text[pos + len(cmd) + 1:].strip()  # +1 for the space
                        break

        # 清理标题，移除可能的标点符号
        if title:
            # 移除开头和结尾的标点符号
            import string
            title = title.strip(string.punctuation + " \t\n\r")

        return {
            "title": title,
            "action": "view",  # 明确标识这是查看操作
            "content": "",  # 查看操作不需要额外内容
            "tags": []
        }

    def _extract_wiki_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取Wiki参数"""
        # 尝试提取页面标题
        title_patterns = [
            r"创建.*wiki.*[:：](.+)",
            r"wiki.*页面[:：](.+)",
            r"编辑.*wiki.*[:：](.+)",
            r"create.*wiki.*[:](.+)",
            r"edit.*wiki.*[:](.+)",
            # 添加对 "wiki create <title>" 模式的支持
            r"wiki\s+create\s+(.+)",
            r"wiki\s+create[:：]\s*(.+)",
        ]

        title = None
        for pattern in title_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                title = m.group(1).strip()
                break

        # 如果没有找到特定标题，使用更智能的方法提取标题
        if not title or title == text:  # 如果title等于原始text，说明没有真正提取到标题
            # 智能提取标题：处理"创建维基 项目计划"、"创建词条 人工智能"这种格式
            # 分割文本并尝试找到标题
            parts = text.split()
            if len(parts) >= 2:  # 如果有至少2个词，就可以尝试智能提取
                # 特殊处理：检查是否包含"词条"、"维基"、"百科"等关键词
                has_target_keyword = any(keyword in text for keyword in ["词条", "维基", "百科", "wiki", "Wiki"])

                # 检查各种可能的创建/编辑/查看命令
                creation_patterns = [
                    "创建维基", "新建维基", "写个维基", "创建百科", "新建百科", "写个百科",
                    "创建词条", "新建词条", "写个词条", "做个词条", "创建条目", "新建条目",
                    "编辑词条", "协同编辑词条", "协同编辑一个词条", "协作编辑词条", "协作编辑一个词条", "编辑维基", "编辑百科", "修改词条", "修改维基", "修改百科",
                    "查看词条", "查看维基", "查看百科", "浏览词条", "浏览维基", "浏览百科"
                ]

                # 更智能的命令检测：直接检查文本中是否包含创建/编辑相关的命令
                is_command_pattern = any(cmd_pattern in text for cmd_pattern in creation_patterns)

                if is_command_pattern and has_target_keyword:
                    # 更智能的标题提取：找到"词条"、"维基"、"百科"等关键词的位置
                    title_parts = []
                    found_keyword = False

                    for i, part in enumerate(parts):
                        if found_keyword:
                            # 已经找到关键词，之后的所有内容都是标题
                            title_parts.append(part)
                        elif any(keyword in part for keyword in ["词条", "维基", "百科", "wiki", "Wiki"]):
                            # 找到关键词
                            found_keyword = True

                    # 如果找到了关键词且后面有内容，提取标题
                    if found_keyword and title_parts:
                        title = " ".join(title_parts).strip()
                    else:
                        # 如果没有找到标题内容，尝试从命令后的词开始提取
                        # 找到第一个包含关键词的词的位置
                        keyword_idx = -1
                        for i, part in enumerate(parts):
                            if any(keyword in part for keyword in ["词条", "维基", "百科", "wiki", "Wiki"]):
                                keyword_idx = i
                                break

                        if keyword_idx >= 0 and keyword_idx < len(parts) - 1:
                            # 取关键词之后的所有词作为标题
                            title = " ".join(parts[keyword_idx + 1:]).strip()
                        elif len(parts) > 2:
                            # 最后的备用方案：取最后几个词作为标题
                            title = " ".join(parts[2:]).strip()

            # 如果还是没有找到标题，检查是否使用了空格分隔的格式
            if not title:
                space_patterns = [
                    (r"创建\s+维基\s+(.+)", r"创建\s*维基\s*(.+)"),
                    (r"新建\s+维基\s+(.+)", r"新建\s*维基\s*(.+)"),
                    (r"写个\s+维基\s+(.+)", r"写个\s*维基\s*(.+)"),
                    (r"创建\s+百科\s+(.+)", r"创建\s*百科\s*(.+)"),
                    (r"新建\s+百科\s+(.+)", r"新建\s*百科\s*(.+)"),
                    (r"写个\s+百科\s+(.+)", r"写个\s*百科\s*(.+)"),
                    # 添加词条相关格式
                    (r"创建\s+词条\s+(.+)", r"创建\s*词条\s*(.+)"),
                    (r"新建\s+词条\s+(.+)", r"新建\s*词条\s*(.+)"),
                    (r"写个\s+词条\s+(.+)", r"写个\s*词条\s*(.+)"),
                    (r"做个\s+词条\s+(.+)", r"做个\s*词条\s*(.+)"),
                    (r"创造\s+词条\s+(.+)", r"创造\s*词条\s*(.+)"),
                    (r"制作\s+词条\s+(.+)", r"制作\s*词条\s*(.+)"),
                    (r"创造\s+维基\s+(.+)", r"创造\s*维基\s*(.+)"),
                    (r"制作\s+维基\s+(.+)", r"制作\s*维基\s*(.+)"),
                    # 添加Wiki相关格式
                    (r"新建\s+wiki\s+(.+)", r"新建\s*wiki\s*(.+)"),
                    (r"创建\s+wiki\s+(.+)", r"创建\s*wiki\s*(.+)"),
                    (r"写个\s+wiki\s+(.+)", r"写个\s*wiki\s*(.+)"),
                    # 特别添加对 "wiki create" 格式的支持
                    (r"wiki\s+create\s+(.+)", r"wiki\s*create\s*(.+)"),
                    # 编辑相关格式
                    (r"编辑\s+词条\s+(.+)", r"编辑\s*词条\s*(.+)"),
                    (r"编辑\s+维基\s+(.+)", r"编辑\s*维基\s*(.+)"),
                    (r"编辑\s+百科\s+(.+)", r"编辑\s*百科\s*(.+)"),
                    # 查看相关格式
                    (r"查看\s+词条\s+(.+)", r"查看\s*词条\s*(.+)"),
                    (r"查看\s+维基\s+(.+)", r"查看\s*维基\s*(.+)"),
                    (r"查看\s+百科\s+(.+)", r"查看\s*百科\s*(.+)"),
                    (r"浏览\s+词条\s+(.+)", r"浏览\s*词条\s*(.+)"),
                    (r"浏览\s+维基\s+(.+)", r"浏览\s*维基\s*(.+)"),
                    (r"浏览\s+百科\s+(.+)", r"浏览\s*百科\s*(.+)"),
                ]

                for pattern, alt_pattern in space_patterns:
                    m = re.search(pattern, text, re.IGNORECASE)
                    if not m:
                        m = re.search(alt_pattern, text, re.IGNORECASE)
                    if m:
                        title = m.group(1).strip()
                        break

            # 专门处理 "wiki create <title>" 的情况
            if not title:
                # 首先检查是否只是 "wiki create" 命令，没有具体标题
                if re.search(r"wiki\s+create\s*$", text.strip(), re.IGNORECASE):
                    title = ""  # 设置为空值以触发澄清
                else:
                    # 查找带标题的 "wiki create <title>" 模式
                    wiki_create_match = re.search(r"wiki\s+create\s+(.+)", text, re.IGNORECASE)
                    if wiki_create_match:
                        title = wiki_create_match.group(1).strip()

            # 检查是否只是通用命令词，如"创建wiki"、"wiki"等
            generic_patterns = [
                r"创建.*wiki",
                r"新建.*wiki",
                r"写.*wiki",
                r"编辑.*wiki",
                r"wiki.*页面",
                r"create.*wiki",
                r"edit.*wiki",
                # 添加中文变体
                r"创建.*维基",
                r"新建.*维基",
                r"写.*维基",
                r"编辑.*维基",
                r"创建.*百科",
                r"新建.*百科",
                r"写.*百科",
                r"创建.*页面",
                r"新建.*页面",
                r"写.*页面",
                # 添加新变体
                r"创造.*维基",
                r"制作.*维基",
                r"创造.*百科",
                r"制作.*百科",
                r"创造.*词条",
                r"制作.*词条",
                r"创造.*wiki",
                r"制作.*wiki",
                # 添加wiki create变体
                r"wiki\s+create"
            ]

            is_generic = any(re.search(pattern, text, re.IGNORECASE) for pattern in generic_patterns)

            # 检查是否是通用命令（只有命令词，没有具体内容）
            # 提取命令操作部分，看是否只有操作词没有具体内容
            command_match = re.search(r'(?:创建|新建|写|写个|做个|创造|制作|编辑|协同编辑|协作编辑)\s*(?:维基|百科|词条|wiki|Wiki)\s*$', text, re.IGNORECASE)
            if is_generic and (not title or command_match or text.strip() in ["创建词条", "新建词条", "写个词条", "做个词条",
                "创造词条", "制作词条", "创建维基", "新建维基", "写个维基", "做个维基", "创造维基", "制作维基",
                "创建百科", "新建百科", "写个百科", "创造百科", "制作百科", "协同编辑一个词条", "协作编辑一个词条",
                "wiki", "wiki create"]):  # 添加对 "wiki create" 作为通用命令的识别
                title = ""  # 设置为空值以触发澄清
            elif not title:  # 如果仍然没有找到标题，使用原始文本
                title = text
            else:
                # 如果title等于原始text，说明没有真正提取到标题，而是匹配了整个命令
                if title == text:
                    title = ""

        return {
            "title": title,
            "content": "",  # 将由用户后续提供
            "tags": []
        }
    
    def _extract_compress_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取压缩参数"""
        return {
            "method": "auto",  # 自动压缩
            "keep_recent": 5   # 保留最近5条对话
        }
    
    def _extract_scaffold_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取项目初始化参数"""
        # 尝试提取项目类型或描述
        type_patterns = [
            r"创建.*(.+?)项目",
            r"初始化.*(.+?)项目",
            r"新建.*(.+?)项目",
            r"create.*(.+?)project",
            r"init.*(.+?)project"
        ]

        project_type = None
        for pattern in type_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                project_type = m.group(1).strip()
                break

        return {
            "project_type": project_type or "general",
            "description": text
        }

    def _extract_knowledge_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取知识库管理参数"""
        return {
            "action": "sync",
            "description": text
        }

    def _extract_knowledge_search_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取知识库搜索参数"""
        # 尝试提取搜索关键词
        search_patterns = [
            r"搜索.*知识库.*[:：\s]*(.+)",
            r"在.*知识库.*搜索[:：\s]*(.+)",
            r"查找.*知识.*[:：\s]*(.+)",
            r"查询.*知识.*[:：\s]*(.+)",
            r"搜索.*[:：\s]*(.+)",
            r"查找.*[:：\s]*(.+)"
        ]

        query = None
        for pattern in search_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                query = m.group(1).strip()
                break

        # 如果没有找到特定关键词，使用整个文本作为查询
        if not query or query.strip() == "":
            # 移除命令词，保留核心搜索词
            cleaned_text = re.sub(r"(搜索|查找|查询|知识库|知识)", "", text, flags=re.IGNORECASE)
            query = cleaned_text.strip()

        return {
            "action": "search",
            "query": query,
            "description": text
        }
    
    def _extract_debate_history_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取辩论历史查询参数"""
        return {
            "query": text,
            "session_id": None  # Will be extracted if specific session is mentioned
        }
    
    def _extract_specific_debate_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取特定辩论查询参数"""
        # Extract session ID or debate ID if present in the match
        session_id = None
        if match.groups():
            session_id = match.group(1)  # First capture group usually contains the ID
        
        # Look for more specific session ID patterns if not already found
        if not session_id:
            session_patterns = [
                r"session[:\s]*([a-zA-Z0-9_-]+)",
                r"debate[:\s]*([a-zA-Z0-9_-]+)",
                r"([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})",  # UUID pattern
            ]
            
            for pattern in session_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    session_id = m.group(1)
                    break
        
        return {
            "query": text,
            "session_id": session_id
        }

    def _extract_skill_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取技能参数"""
        # 首先尝试从文本中提取技能相关参数
        skill_patterns = [
            # 专门的技能请求 - 明确的关键词后跟内容
            r".*[执行|运行|使用].*技能[:：]\s*(.+?)$",
            r".*[帮我|请帮我].*[:：]\s*([^。？！]+)$",
            # 文本处理相关 - 直接提取文本内容
            r".*[帮助|帮我|请帮我].*分析\s+(.+?)[。？！]*$",
            r".*[帮助|帮我|请帮我].*处理\s+(.+?)[。？！]*$",
            r".*[帮助|帮我|请帮我].*搜索\s+(.+?)[。？！]*$",
            r".*[帮助|帮我|请帮我].*查找\s+(.+?)[。？！]*$",
            r".*[帮助|帮我|请帮我].*总结\s+(.+?)[。？！]*$",
            r".*[帮助|帮我|请帮我].*写\s+(.+?)[。？！]*$",
            # 通用技能请求
            r".*分析\s+(.+?)[。？！]*$",
            r".*处理\s+(.+?)[。？！]*$",
            r".*搜索\s+(.+?)[。？！]*$",
            r".*查找\s+(.+?)[。？！]*$",
            r".*总结\s+(.+?)[。？！]*$",
            # 关于/对某事物的模式
            r".*关于\s+(.+?)\s+(进行|执行|分析|搜索|查找|处理|研究|总结)",
            r".*对\s+(.+?)\s+(进行|执行|分析|搜索|查找|处理|研究|总结)",
            r".*在\s+(.+?)\s+(中|方面|领域)\s+(进行|执行|分析|搜索|查找|处理|研究|总结)",
            # 给我XX的模式
            r".*给我.*分析\s+(.+?)[。？！]*$",
            r".*给我.*处理\s+(.+?)[。？！]*$",
            r".*给我.*搜索\s+(.+?)[。？！]*$",
            r".*给我.*查找\s+(.+?)[。？！]*$",
        ]

        # 查找具体技能内容
        skill_content = ""
        for pattern in skill_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m and m.groups() and len(m.groups()) > 0:
                extracted = m.group(1).strip()  # 提取第一个捕获组
                if extracted and len(extracted) > 1 and extracted != text.strip():
                    skill_content = extracted
                    break

        # 如果没有找到特定技能内容，使用更智能的方法提取内容
        if not skill_content or skill_content == "":
            # 智能提取文本内容的模式
            intelligent_patterns = [
                r".*帮我.*分析[关于|的|这]*\s*([^。、？！]+)",   # "帮我分析关于人工智能的发展趋势"
                r".*帮我.*处理[关于|这]*\s*([^。、？！]+)",   # "帮我处理这个文档"
                r".*帮我.*搜索[关于|这]*\s*([^。、？！]+)",   # "帮我搜索机器学习资料"
                r".*帮我.*查找[关于|这]*\s*([^。、？！]+)",   # "帮我查找资料"
                r".*帮我.*总结[关于|这]*\s*([^。、？！]+)",   # "帮我总结论文"
                r".*分析[一下|下|这个]*\s*([^。、？！]+)",   # "分析一下人工智能"
                r".*处理[这个|这些]*\s*([^。、？！]+)",      # "处理这个资料"
                r".*搜索[关于|这]*\s*([^。、？！]+)",       # "搜索量子计算资料"
                r".*查找[这些|这个|相关]*\s*([^。、？！]+)",  # "查找这些文献"
                r".*总结[这个|这份|这篇]*\s*([^。、？！]+)",  # "总结这份报告"
                r".*帮我.*([一|一|一下|些|这个|这些|那份].+?)[。、？！]*",  # "帮我一下XXX"
                r".*(写|分析|处理|搜索|查找|总结).*(.+?)[。、？！]*",  # "帮我写人工智能"
            ]

            for pattern in intelligent_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m and m.groups():
                    extracted = m.group(1).strip()
                    if extracted and len(extracted) > 1 and extracted != text.strip():
                        # 检查提取的内容是否包含命令词
                        if not any(cmd.strip() == extracted for cmd in ["帮我", "请帮我", "分析", "处理", "搜索", "查找", "总结"]):
                            skill_content = extracted
                            break

        # 如果仍为空，尝试从命令词后提取内容
        if not skill_content or skill_content == "":
            # 移除常见的技能提示词，保留后面的内容
            command_words = [
                "帮我", "请帮我", "帮我分析", "帮我处理", "帮我搜索", "帮我查找",
                "帮我总结", "帮我写", "帮我生成", "帮我翻译", "帮我整理",
                "帮我创建", "请分析", "请处理", "请搜索", "请查找", "请总结",
                "执行", "运行", "使用", "启动", "开始", "分析", "处理", "搜索",
                "查找", "总结", "生成", "翻译", "创建", "写个", "做个",
                "创建维基", "新建百科", "写百科", "编辑页面", "创建页面",
                "文本分析", "文档处理", "内容搜索", "信息查找", "知识搜索",
                "给", "给我", "给我分析", "给我处理", "给我搜索", "给我查找"
            ]

            # 按长度排序，优先匹配长命令词
            sorted_commands = sorted(command_words, key=len, reverse=True)

            original_text = text.strip()
            for cmd in sorted_commands:
                if original_text.startswith(cmd.lower()) or original_text.startswith(cmd):
                    # 提取命令词后面的内容
                    potential_content = original_text[len(cmd):].strip()
                    if potential_content and len(potential_content) > 3:  # 至少3个字符才是有效内容
                        # 检查是否是纯命令词
                        if potential_content not in command_words:
                            skill_content = potential_content
                        break
                elif cmd.lower() in original_text.lower():
                    # 在文本中找到命令词，提取其后面的内容
                    pos = original_text.lower().find(cmd.lower())
                    if pos != -1:
                        potential_content = original_text[pos + len(cmd):].strip()
                        if potential_content and len(potential_content) > 3:
                            # 检查是否是纯命令词
                            if potential_content not in command_words:
                                skill_content = potential_content
                                break

        # 如果仍然找不到内容，skill_content保持为空字符串
        if not skill_content:
            skill_content = ""

        # 识别期望的技能类型
        skill_type = "general"
        if any(keyword in text.lower() for keyword in ["分析", "analyze", "text", "内容", "文档"]):
            skill_type = "analysis"
        elif any(keyword in text.lower() for keyword in ["处理", "process", "文档", "document", "文本"]):
            skill_type = "processing"
        elif any(keyword in text.lower() for keyword in ["搜索", "查找", "search", "find", "资料", "信息", "论文"]):
            skill_type = "search"
        elif any(keyword in text.lower() for keyword in ["写作", "write", "create", "撰写", "创建", "生成"]):
            skill_type = "writing"
        elif any(keyword in text.lower() for keyword in ["翻译", "translate", "translation"]):
            skill_type = "translation"
        elif any(keyword in text.lower() for keyword in ["总结", "summarize", "摘要", "概括"]):
            skill_type = "summarization"
        elif any(keyword in text.lower() for keyword in ["问答", "question", "answer", "问", "答"]):
            skill_type = "question_answering"
        elif any(keyword in text.lower() for keyword in ["规划", "planning", "安排", "策略"]):
            skill_type = "planning"
        elif any(keyword in text.lower() for keyword in ["助手", "assistant", "智能", "AI"]):
            skill_type = "assistant"
        elif any(keyword in text.lower() for keyword in ["维基", "wiki", "百科"]):
            skill_type = "wiki_creation"
        elif any(keyword in text.lower() for keyword in ["技能", "skill", "工具", "tool"]):
            skill_type = "general_skill"

        # 如果skill_content为空且text包含足够信息，使用text作为skill_content
        if not skill_content and len(text.strip()) > 5:
            # 检查是否只是命令词，如果不是，则使用原文本作为内容
            is_just_command = any(text.strip() == cmd or text.strip().startswith(cmd) for cmd in command_words)
            if not is_just_command:
                skill_content = text

        # 增强技能匹配逻辑 - 尝试根据技能管理器中的可用技能匹配
        target_skill_name = skill_type  # 默认技能类型
        if self.skill_manager:  # 如果技能管理器可用
            available_skills = self.skill_manager.list_skills()

            # 尝试根据用户输入的意图匹配最相关的技能
            for skill_name in available_skills:
                # 检查技能名称是否在用户输入中
                if skill_name.lower() in text.lower():
                    target_skill_name = skill_name
                    break
                # 检查技能是否匹配输入中的关键词
                elif skill_name == "text_analysis" and any(kw in text.lower() for kw in ["分析", "analyze", "text", "内容"]):
                    target_skill_name = skill_name
                    break
                elif skill_name == "search" and any(kw in text.lower() for kw in ["搜索", "查找", "find", "search"]):
                    target_skill_name = skill_name
                    break
                elif skill_name == "writing" and any(kw in text.lower() for kw in ["写", "写作", "create", "write"]):
                    target_skill_name = skill_name
                    break
                elif skill_name == "translation" and any(kw in text.lower() for kw in ["翻译", "translate"]):
                    target_skill_name = skill_name
                    break
                elif skill_name == "summarization" and any(kw in text.lower() for kw in ["总结", "摘要", "summarize"]):
                    target_skill_name = skill_name
                    break
                elif skill_name == "calculation" and any(kw in text.lower() for kw in ["计算", "计算", "算", "math"]):
                    target_skill_name = skill_name
                    break

        # 如果找到了匹配的技能名称，更新skill_type
        if target_skill_name in available_skills:
            skill_type = target_skill_name

        return {
            "target_skill": skill_type,
            "content": skill_content,
            "original_request_text": text,  # 修正字段名
            "parameters": {
                "content_to_analyze": skill_content if skill_content else text,
                "skill_type": skill_type
            }
        }

    def _extract_assistant_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取助手参数"""
        # 确定助手的具体请求类型
        request_type = "general_assistance"  # 默认通用助手请求

        # 检查具体意图
        if any(keyword in text.lower() for keyword in ["分析", "总结", "search", "find", "search", "find", "searching", "finding"]):
            request_type = "research_assistance"
        elif any(keyword in text.lower() for keyword in ["写", "create", "generate", "draft", "make"]):
            request_type = "content_creation"
        elif any(keyword in text.lower() for keyword in ["翻译", "translate", "translation", "convert"]):
            request_type = "translation"
        elif any(keyword in text.lower() for keyword in ["解释", "explain", "understand", "understanding"]):
            request_type = "explanation"
        elif any(keyword in text.lower() for keyword in ["帮助", "help", "assist", "assist"]):
            request_type = "help_request"

        # 尝试提取具体请求内容
        content_parts = []
        if ":" in text:
            content_parts = text.split(":")[1:]
        elif "，" in text:
            content_parts = text.split("，")[1:]
        elif "。" in text:
            content_parts = text.split("。")[1:]
        else:
            # 提取助手指令后的内容
            for keyword in ["助手", "助理", "AI", "PA"]:
                if keyword in text:
                    idx = text.find(keyword)
                    if idx != -1:
                        content = text[idx + len(keyword):].strip()
                        if content:
                            content_parts = [content]
                        break

        specific_request = content_parts[0] if content_parts else text

        return {
            "request_type": request_type,
            "specific_request": specific_request.strip() if specific_request else text,
            "original_request": text,
            "use_knowledge_base": True,  # 默认启用知识库检索
            "multi_model_required": True  # 默认启用多模型协作
        }

    def _extract_skill_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取技能参数"""
        skill_params = {}

        # 确定技能类型
        skill_type = "general"

        if any(keyword in text.lower() for keyword in ["分析", "analyze", "analyze", "text_analysis", "文本分析"]):
            skill_type = "text_analysis"
        elif any(keyword in text.lower() for keyword in ["搜索", "查找", "search", "find", "检索"]):
            skill_type = "search"
        elif any(keyword in text.lower() for keyword in ["创建", "create", "write", "写", "生成", "generate"]):
            skill_type = "content_creation"
        elif any(keyword in text.lower() for keyword in ["处理", "process", "convert", "转换"]):
            skill_type = "processing"
        elif any(keyword in text.lower() for keyword in ["助手", "assistant", "AI", "智能"]):
            skill_type = "assistant"

        skill_params["skill_type"] = skill_type

        # 提取技能内容或参数
        content = None
        extract_patterns = [
            r"分析.*[:：\s]*(.+)",
            r"处理.*[:：\s]*(.+)",
            r"帮我.*[:：\s]*(.+)",
            r".*分析.*[:：\s]*(.+)",
            r"执行.*[:：\s]*(.+)",
            r"运行.*[:：\s]*(.+)",
            r"关于.*[:：\s]*(.+)",
            r".*[主题|内容|文本|资料].*[:：\s]*(.+)"
        ]

        for pattern in extract_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                content = m.group(1).strip()
                break

        if not content:
            # 如果没有找到特定内容，尝试从整个文本中提取有意义的部分
            # 移除功能词，保留内容词
            functional_words = ["帮我", "请", "帮我分析", "帮我处理", "我想", "我想让", "执行", "运行"]
            content = text
            for word in functional_words:
                content = content.replace(word, "").strip()

        skill_params["content"] = content if content else ""
        skill_params["original_request"] = text

        # 确定是否需要额外的澄清
        skill_params["requires_clarification"] = not bool(content.strip()) if content else True

        return skill_params

    def _extract_complex_task_params(self, text: str, match: re.Match) -> Dict[str, Any]:
        """提取复杂任务参数"""
        # 复杂任务通常就是整个用户请求
        return {
            "original_request": text,
            "task_description": text,
            "task_type": self._determine_complex_task_type(text),
            "requires_clarification": False  # 复杂任务通常不需要额外澄清
        }

    def _determine_complex_task_type(self, text: str) -> str:
        """确定复杂任务类型"""
        text_lower = text.lower()

        # 根据关键词确定任务类型
        if any(keyword in text_lower for keyword in ["分析", "研究", "调研", "调查"]):
            return "analysis"
        elif any(keyword in text_lower for keyword in ["设计", "架构", "构建", "开发"]):
            return "design"
        elif any(keyword in text_lower for keyword in ["创建", "撰写", "编写", "制作"]):
            return "creation"
        elif any(keyword in text_lower for keyword in ["评估", "比较", "对比", "评价"]):
            return "evaluation"
        elif any(keyword in text_lower for keyword in ["规划", "计划", "策略", "方案"]):
            return "planning"
        elif any(keyword in text_lower for keyword in ["解决方案", "解决", "应对"]):
            return "solution"
        else:
            return "general"

    def get_available_intents(self) -> List[str]:
        """获取所有可用的意图列表"""
        return list(self.intent_patterns.keys())

    def get_intent_description(self, intent_name: str) -> str:
        """获取意图描述"""
        if intent_name in self.intent_patterns:
            return self.intent_patterns[intent_name]["description"]
        return "未知意图"