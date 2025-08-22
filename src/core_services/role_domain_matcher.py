#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色专业领域匹配算法实现
"""

import re
from typing import List, Dict, Set
from src.core_services.role_manager import RoleManager


class RoleDomainMatcher:
    """角色专业领域匹配器"""
    
    def __init__(self, role_manager: RoleManager = None):
        """初始化匹配器"""
        self.role_manager = role_manager or RoleManager()
        
        # 定义停用词
        self.stop_words = {
            "的", "和", "与", "及", "以及", "或者", "还是", "但是", "然而", "因此", 
            "所以", "为了", "关于", "对于", "通过", "基于", "利用", "采用", "一个",
            "这个", "那个", "这些", "那些", "一些", "很多", "全部", "所有", "每个",
            "任何", "某些", "其他", "另外", "此外", "而且", "然而", "但是", "可是",
            "不过", "总之", "最后", "首先", "其次", "然后", "接着", "同时", "一起",
            "共同", "分别", "各自", "互相", "相互", "彼此", "自己", "我们", "你们",
            "他们", "她们", "它们", "人们", "人类", "个人", "集体", "组织", "机构",
            "公司", "企业", "政府", "国家", "社会", "世界", "全球", "国际", "国内",
            "地方", "地区", "城市", "乡村", "环境", "自然", "科学", "技术", "工程",
            "医学", "健康", "教育", "学习", "研究", "开发", "设计", "制造", "生产",
            "管理", "经营", "运营", "服务", "提供", "使用", "应用", "实施", "执行",
            "完成", "实现", "达到", "获得", "取得", "得到", "拥有", "具备", "具有",
            "包含", "包括", "涵盖", "涉及", "关联", "相关", "有关", "对应", "针对",
            "处理", "解决", "分析", "评估", "评价", "审查", "检查", "检验", "测试",
            "实验", "试验", "验证", "确认", "证明", "表明", "显示", "展示", "呈现",
            "表现", "表达", "描述", "说明", "解释", "阐述", "论述", "讨论", "探讨",
            "研究", "调查", "考察", "观察", "监视", "监控", "监测", "检测", "诊断",
            "治疗", "治愈", "预防", "防护", "保护", "保障", "确保", "保证", "承诺",
            "负责", "承担", "履行", "执行", "贯彻", "落实", "推进", "促进", "推动",
            "发展", "进步", "提升", "提高", "增强", "加强", "改进", "改善", "改良",
            "改革", "革新", "创新", "创造", "创建", "建立", "建设", "构建", "组成",
            "构成", "形成", "造成", "导致", "引起", "引发", "产生", "发生", "出现",
            "存在", "拥有", "持有", "保有", "维持", "保持", "保留", "保存", "储存",
            "存储", "存放", "安置", "安排", "布置", "配置", "分配", "分派", "分工",
            "合作", "协作", "协同", "配合", "协调", "调整", "调节", "调控", "控制",
            "掌握", "把握", "了解", "理解", "明白", "知道", "认识", "认知", "感知",
            "感觉", "感受", "体验", "经历", "经验", "教训", "启示", "启发", "灵感",
            "创意", "想法", "思路", "思维", "思想", "理念", "观念", "观点", "看法",
            "意见", "建议", "提议", "提案", "方案", "计划", "规划", "策划", "策略",
            "战略", "战术", "方法", "方式", "形式", "模式", "模型", "模板", "样本",
            "例子", "示例", "实例", "案例", "问题", "难题", "困难", "挑战", "机遇",
            "机会", "可能性", "概率", "风险", "危险", "威胁", "危害", "损害", "伤害",
            "损伤", "破坏", "损坏", "故障", "错误", "失误", "缺陷", "不足", "缺点",
            "劣势", "弱点", "短处", "劣势", "优势", "长处", "优点", "好处", "利益",
            "收益", "效益", "效果", "成果", "结果", "结局", "目的", "目标", "宗旨",
            "意图", "意愿", "愿望", "希望", "期望", "期待", "要求", "需求", "需要",
            "必要", "必须", "应该", "应当", "可以", "可能", "也许", "大概", "或许",
            "似乎", "好像", "仿佛", "如同", "类似", "一样", "相同", "相等", "等于",
            "等同", "等价", "相当", "适合", "合适", "适宜", "适当", "恰当", "得当",
            "正确", "准确", "精确", "精准", "精细", "细致", "详细", "具体", "明确",
            "清楚", "清晰", "鲜明", "显著", "明显", "突出", "重要", "主要", "关键",
            "核心", "中心", "中央", "中间", "内部", "内在", "里面", "外部", "外面",
            "外表", "表面", "外观", "形状", "形态", "形式", "格式", "样式", "类型",
            "种类", "类别", "分类", "等级", "层次", "级别", "程度", "水平", "标准",
            "规范", "规则", "规定", "制度", "体系", "系统", "机制", "体制", "结构",
            "构造", "组成", "成分", "元素", "要素", "因子", "因素", "原因", "理由",
            "根据", "依据", "基础", "根本", "基本", "根本", "本质", "实质", "实际",
            "现实", "事实", "实际", "真实", "真正", "真正", "确实", "的确", "的确",
            "当然", "当然", "自然", "自然", "必然", "必然", "肯定", "肯定", "确定",
            "确定", "决定", "决定", "决策", "决策", "选择", "选择", "挑选", "挑选",
            "选取", "选取", "选定", "选定", "选举", "选举", "投票", "投票", "表决",
            "表决", "同意", "同意", "赞成", "赞成", "支持", "支持", "拥护", "拥护",
            "反对", "反对", "拒绝", "拒绝", "否定", "否定", "否认", "否认", "取消",
            "取消", "撤销", "撤销", "废除", "废除", "删除", "删除", "去除", "去除",
            "去掉", "去掉", "排除", "排除", "排除", "排除", "消除", "消除", "消灭",
            "消灭", "结束", "结束", "完成", "完成", "完毕", "完毕", "终止", "终止",
            "停止", "停止", "暂停", "暂停", "中断", "中断", "打断", "打断", "破坏",
            "破坏", "损坏", "损坏", "毁坏", "毁坏", "摧毁", "摧毁", "摧毁", "摧毁",
            "攻击", "攻击", "打击", "打击", "袭击", "袭击", "侵犯", "侵犯", "侵害",
            "侵害", "伤害", "伤害", "损害", "损害", "损失", "损失", "丢失", "丢失",
            "遗失", "遗失", "忘记", "忘记", "遗忘", "遗忘", "忽略", "忽略", "忽视",
            "忽视", "疏忽", "疏忽", "失误", "失误", "错误", "错误", "谬误", "谬误",
            "偏差", "偏差", "偏离", "偏离", "偏移", "偏移", "偏转", "偏转", "倾斜",
            "倾斜", "弯曲", "弯曲", "曲折", "曲折", "复杂", "复杂", "简单", "简单",
            "容易", "容易", "困难", "困难", "艰难", "艰难", "艰苦", "艰苦", "辛苦",
            "辛苦", "劳累", "劳累", "疲劳", "疲劳", "疲倦", "疲倦", "疲惫", "疲惫",
            "困倦", "困倦", "困乏", "困乏", "饥饿", "饥饿", "口渴", "口渴", "寒冷",
            "寒冷", "炎热", "炎热", "温暖", "温暖", "凉爽", "凉爽", "舒适", "舒适",
            "舒服", "舒服", "愉快", "愉快", "快乐", "快乐", "高兴", "高兴", "喜悦",
            "喜悦", "欢乐", "欢乐", "欢欣", "欢欣", "兴奋", "兴奋", "激动", "激动",
            "感动", "感动", "感激", "感激", "感谢", "感谢", "感恩", "感恩", "抱歉",
            "抱歉", "对不起", "对不起", "道歉", "道歉", "遗憾", "遗憾", "失望", "失望",
            "绝望", "绝望", "沮丧", "沮丧", "郁闷", "郁闷", "烦恼", "烦恼", "焦虑",
            "焦虑", "担心", "担心", "忧虑", "忧虑", "恐惧", "恐惧", "害怕", "害怕",
            "畏惧", "畏惧", "胆怯", "胆怯", "怯懦", "怯懦", "勇敢", "勇敢", "英勇",
            "英勇", "无畏", "无畏", "坚强", "坚强", "坚韧", "坚韧", "坚毅", "坚毅",
            "毅力", "毅力", "耐力", "耐力", "耐心", "耐心", "忍耐", "忍耐", "宽容",
            "宽容", "包容", "包容", "容忍", "容忍", "原谅", "原谅", "宽恕", "宽恕",
            "慈悲", "慈悲", "仁慈", "仁慈", "善良", "善良", "和善", "和善", "友好",
            "友好", "友善", "友善", "亲切", "亲切", "亲热", "亲热", "热情", "热情",
            "热心", "热心", "积极", "积极", "主动", "主动", "被动", "被动", "消极",
            "消极", "悲观", "悲观", "乐观", "乐观", "希望", "希望", "绝望", "绝望",
            "信心", "信心", "信念", "信念", "信仰", "信仰", "宗教", "宗教", "哲学",
            "哲学", "思想", "思想", "理论", "理论", "学说", "学说", "观点", "观点",
            "看法", "看法", "意见", "意见", "建议", "建议", "忠告", "忠告", "劝告",
            "劝告", "警告", "警告", "提醒", "提醒", "通知", "通知", "告知", "告知",
            "告诉", "告诉", "说明", "说明", "解释", "解释", "阐述", "阐述", "论述",
            "论述", "论证", "论证", "证明", "证明", "证实", "证实", "验证", "验证",
            "检验", "检验", "检查", "检查", "审查", "审查", "审核", "审核", "核实",
            "核实", "确认", "确认", "确定", "确定", "决定", "决定", "决策", "决策"
        }
        
        # 领域同义词映射
        self.domain_synonyms = {
            # 生物信息学领域
            "生物信息学": ["计算生物学", "生物数据科学", "生物计算"],
            "基因组学": ["基因学", "DNA分析", "基因组分析"],
            "蛋白质组学": ["蛋白质学", "蛋白组分析"],
            
            # 环境经济学领域
            "环境经济学": ["生态经济学", "环境经济分析"],
            "自然资源": ["自然资源管理", "资源经济学"],
            "气候变化": ["全球变暖", "气候变迁"],
            
            # 神经科学领域
            "神经科学": ["神经学", "脑科学", "神经生物学"],
            "认知神经科学": ["认知神经学", "脑认知"],
            "计算神经科学": ["理论神经科学", "神经建模"],
            
            # 材料科学领域
            "纳米材料": ["纳米技术", "纳米科学"],
            "能源材料": ["能量材料", "动力材料"],
            "生物材料": ["生物医学材料", "医用材料"],
            
            # 金融工程领域
            "金融工程": ["金融技术", "量化金融"],
            "量化分析": ["数量分析", "量化金融"],
            "算法交易": ["程序化交易", "自动交易"],
            
            # 认知科学领域
            "认知科学": ["认知研究", "心智科学"],
            "人工智能伦理": ["AI伦理", "机器伦理"],
            "语言认知": ["语言心理", "语言心智"],
            
            # 城市规划领域
            "智慧城市": ["智能城市", "数字城市"],
            "交通系统": ["交通运输", "交通网络"],
            "社区发展": ["社区建设", "社区规划"],
            
            # 网络安全领域
            "网络安全": ["信息安全", "网络防护"],
            "渗透测试": ["渗透检测", "安全测试"],
            "安全运维": ["安全运营", "安全维护"],
            
            # 生物医学工程领域
            "生物医学工程": ["生物工程", "医学工程"],
            "生物信号": ["生理信号", "生物电信号"],
            "组织工程": ["组织再生", "再生医学"],
            
            # 教育技术领域
            "教育技术": ["教育科技", "学习技术"],
            "学习体验": ["学习设计", "教学设计"],
            "在线学习": ["网络学习", "远程学习"]
        }
        
        # 初始化角色领域映射
        self.role_domains = self._initialize_role_domains()
    
    def _initialize_role_domains(self) -> Dict[str, List[str]]:
        """初始化角色领域映射"""
        role_domains = {}
        
        # 获取所有角色
        roles = self.role_manager.list_roles()
        
        # 为每个角色提取领域关键词
        for role in roles:
            domains = []
            
            # 从角色名称中提取领域关键词
            if role.name:
                domains.extend(self.extract_keywords(role.name))
            
            # 从角色描述中提取领域关键词
            if role.description:
                domains.extend(self.extract_keywords(role.description))
            
            # 从角色能力中提取领域关键词
            if role.capabilities:
                for capability in role.capabilities:
                    domains.extend(self.extract_keywords(capability))
            
            # 从角色标签中提取领域关键词
            if role.tags:
                domains.extend(self.extract_keywords(" ".join(role.tags)))
            
            # 去重并保存
            role_domains[role.id] = list(set(domains))
        
        return role_domains
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            
        Returns:
            关键词列表
        """
        if not text:
            return []
        
        # 清理文本
        # 移除特殊字符和标点符号，但保留中文字符
        cleaned_text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        
        # 分词并过滤
        words = [word.strip() for word in cleaned_text.split() if word.strip()]
        keywords = [word for word in words if word not in self.stop_words and len(word) > 1]
        
        # 扩展同义词
        extended_keywords = set(keywords)
        for keyword in keywords:
            # 查找直接匹配的同义词
            if keyword in self.domain_synonyms:
                extended_keywords.update(self.domain_synonyms[keyword])
            
            # 查找反向匹配的同义词
            for primary_term, synonyms in self.domain_synonyms.items():
                if keyword in synonyms:
                    extended_keywords.add(primary_term)
                    extended_keywords.update(synonyms)
        
        return list(extended_keywords)
    
    def calculate_match_score(self, keywords: List[str], domains: List[str]) -> float:
        """
        计算关键词与领域列表的匹配度
        
        Args:
            keywords: 关键词列表
            domains: 领域列表
            
        Returns:
            匹配度分数 (0-1)
        """
        if not keywords or not domains:
            return 0.0
        
        # 计算关键词在领域中的出现次数
        match_count = 0
        total_weight = 0
        
        for keyword in keywords:
            keyword_weight = 1.0
            # 给较长的关键词更高的权重
            if len(keyword) > 3:
                keyword_weight = 1.5
            elif len(keyword) > 5:
                keyword_weight = 2.0
                
            total_weight += keyword_weight
            
            for domain in domains:
                # 精确匹配
                if keyword == domain:
                    match_count += 2 * keyword_weight  # 精确匹配权重更高
                # 包含匹配
                elif keyword in domain or domain in keyword:
                    match_count += 1 * keyword_weight
        
        # 计算匹配度分数
        if total_weight == 0:
            return 0.0
            
        score = match_count / total_weight
        return min(score, 1.0)  # 确保不超过1.0
    
    def match_roles_to_task(self, task_description: str, max_roles: int = 3) -> List[str]:
        """
        根据任务描述匹配最合适的角色
        
        Args:
            task_description: 任务描述
            max_roles: 最大返回角色数
            
        Returns:
            匹配的角色ID列表
        """
        # 1. 提取关键词
        keywords = self.extract_keywords(task_description)
        
        if not keywords:
            # 如果没有提取到关键词，返回默认角色
            return ["ai_ethicist", "cognitive_neuroscientist", "quantitative_analyst"]
        
        # 2. 计算角色匹配度
        role_scores = {}
        for role_id, domains in self.role_domains.items():
            score = self.calculate_match_score(keywords, domains)
            role_scores[role_id] = score
        
        # 3. 按匹配度排序并选择前N个角色
        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        selected_roles = [role_id for role_id, score in sorted_roles if score > 0][:max_roles]
        
        # 如果没有匹配到角色，返回默认角色
        if not selected_roles:
            return ["ai_ethicist", "cognitive_neuroscientist", "quantitative_analyst"]
        
        return selected_roles
    
    def get_role_matching_details(self, task_description: str, max_roles: int = 3) -> Dict:
        """
        获取角色匹配的详细信息
        
        Args:
            task_description: 任务描述
            max_roles: 最大返回角色数
            
        Returns:
            包含匹配详情的字典
        """
        # 1. 提取关键词
        keywords = self.extract_keywords(task_description)
        
        # 2. 计算角色匹配度
        role_scores = {}
        role_details = {}
        
        for role_id, domains in self.role_domains.items():
            score = self.calculate_match_score(keywords, domains)
            role_scores[role_id] = score
            
            # 获取角色详细信息
            role = self.role_manager.get_role(role_id)
            if role:
                role_details[role_id] = {
                    "name": role.name,
                    "description": role.description,
                    "domains": domains,
                    "score": score
                }
        
        # 3. 按匹配度排序并选择前N个角色
        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        selected_roles = [role_id for role_id, score in sorted_roles if score > 0][:max_roles]
        
        return {
            "task_keywords": keywords,
            "matched_roles": [
                role_details[role_id] for role_id in selected_roles
            ],
            "all_scores": sorted_roles[:10]  # 返回前10个角色的分数
        }


# 测试代码
if __name__ == "__main__":
    # 创建匹配器
    matcher = RoleDomainMatcher()
    
    # 测试用例
    test_cases = [
        "创建一个关于基因编辑技术的Wiki词条",
        "分析气候变化对金融市场的影响",
        "设计一个智能交通管理系统",
        "开发新的抗癌药物",
        "评估人工智能在教育中的应用",
        "研究大脑如何处理语言信息"
    ]
    
    print("角色专业领域匹配测试:")
    print("=" * 50)
    
    for i, task in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {task}")
        matched_roles = matcher.match_roles_to_task(task, 3)
        print(f"匹配角色: {matched_roles}")
        
        # 获取详细信息
        details = matcher.get_role_matching_details(task, 3)
        print(f"关键词: {details['task_keywords']}")
        
        for role in details['matched_roles']:
            print(f"  - {role['name']} (匹配度: {role['score']:.3f})")