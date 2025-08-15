#!/usr/bin/env python3
"""学术写作辅助工具

V0.2.3 - 学术研究场景核心功能
提供全面的学术写作指导和辅助功能
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from src.scenarios.enhanced_academic_research_scenario import WritingSection

logger = logging.getLogger(__name__)


class WritingSectionType(Enum):
    """写作章节类型"""
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    LITERATURE_REVIEW = "literature_review"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    APPENDIX = "appendix"


class WritingStyle(Enum):
    """写作风格"""
    ACADEMIC_FORMAL = "academic_formal"
    SCIENTIFIC_REPORT = "scientific_report"
    CONFERENCE_PAPER = "conference_paper"
    JOURNAL_ARTICLE = "journal_article"
    THESIS_DISSERTATION = "thesis_dissertation"
    GRANT_PROPOSAL = "grant_proposal"


class CitationStyle(Enum):
    """引用格式"""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"
    HARVARD = "harvard"
    VANCOUVER = "vancouver"


@dataclass
class WritingGuideline:
    """写作指导"""
    section_type: WritingSectionType
    purpose: str
    structure: list[str]
    key_elements: list[str]
    word_count_range: tuple[int, int]
    common_mistakes: list[str]
    best_practices: list[str]
    example_phrases: list[str]


@dataclass
class WritingFeedback:
    """写作反馈"""
    section_type: WritingSectionType
    overall_score: float
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    grammar_issues: list[str]
    style_issues: list[str]
    structure_feedback: str
    clarity_score: float
    coherence_score: float
    academic_tone_score: float


@dataclass
class Citation:
    """引用"""
    authors: list[str]
    title: str
    year: int
    venue: str
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citation_type: str = "journal"


class AcademicWritingAssistant:
    """学术写作辅助工具"""
    
    def __init__(self):
        self.writing_guidelines = self._initialize_writing_guidelines()
        self.style_templates = self._initialize_style_templates()
        self.citation_formatters = self._initialize_citation_formatters()
        
        logger.info("Academic Writing Assistant initialized")
    
    def _initialize_writing_guidelines(self) -> dict[WritingSectionType, WritingGuideline]:
        """初始化写作指导"""
        return {
            WritingSectionType.ABSTRACT: WritingGuideline(
                section_type=WritingSectionType.ABSTRACT,
                purpose="Provide a concise summary of the entire research study",
                structure=[
                    "Background/Context",
                    "Research Problem/Objective", 
                    "Methods",
                    "Key Results",
                    "Conclusions/Implications"
                ],
                key_elements=[
                    "Clear research question",
                    "Brief methodology description",
                    "Main findings",
                    "Significance of results",
                    "No citations typically"
                ],
                word_count_range=(150, 300),
                common_mistakes=[
                    "Too much background information",
                    "Vague or missing results",
                    "Including citations",
                    "Exceeding word limit",
                    "Using abbreviations without definition"
                ],
                best_practices=[
                    "Write the abstract last",
                    "Use past tense for completed work",
                    "Be specific about findings",
                    "Avoid jargon and abbreviations",
                    "Make it self-contained"
                ],
                example_phrases=[
                    "This study investigated...",
                    "The purpose of this research was to...",
                    "Results showed that...",
                    "These findings suggest...",
                    "The implications of this study are..."
                ]
            ),
            
            WritingSectionType.INTRODUCTION: WritingGuideline(
                section_type=WritingSectionType.INTRODUCTION,
                purpose="Establish the research context, problem, and objectives",
                structure=[
                    "General topic introduction",
                    "Literature context",
                    "Research gap identification",
                    "Research questions/hypotheses",
                    "Study significance"
                ],
                key_elements=[
                    "Hook to engage readers",
                    "Background information",
                    "Literature synthesis",
                    "Clear research gap",
                    "Specific objectives"
                ],
                word_count_range=(800, 1500),
                common_mistakes=[
                    "Too broad or too narrow scope",
                    "Insufficient literature integration",
                    "Unclear research questions",
                    "Missing significance statement",
                    "Poor flow between paragraphs"
                ],
                best_practices=[
                    "Start broad, then narrow down",
                    "Use funnel structure",
                    "Integrate literature critically",
                    "State objectives clearly",
                    "End with study overview"
                ],
                example_phrases=[
                    "Recent advances in... have highlighted...",
                    "Despite extensive research on..., little is known about...",
                    "This study addresses this gap by...",
                    "The primary objective of this research is to...",
                    "Understanding this phenomenon is crucial because..."
                ]
            ),
            
            WritingSectionType.METHODOLOGY: WritingGuideline(
                section_type=WritingSectionType.METHODOLOGY,
                purpose="Describe research design and procedures in sufficient detail for replication",
                structure=[
                    "Research design overview",
                    "Participants/Sample",
                    "Materials/Instruments",
                    "Procedures",
                    "Data analysis plan"
                ],
                key_elements=[
                    "Detailed research design",
                    "Sample description",
                    "Data collection methods",
                    "Analysis procedures",
                    "Ethical considerations"
                ],
                word_count_range=(1000, 2000),
                common_mistakes=[
                    "Insufficient detail for replication",
                    "Missing ethical approval information",
                    "Unclear sampling procedures",
                    "Inadequate instrument description",
                    "No justification for methods chosen"
                ],
                best_practices=[
                    "Use past tense throughout",
                    "Provide sufficient detail",
                    "Justify methodological choices",
                    "Include ethical considerations",
                    "Use subheadings for clarity"
                ],
                example_phrases=[
                    "A [design type] design was employed to...",
                    "Participants were recruited through...",
                    "Data were collected using...",
                    "The analysis was conducted using...",
                    "Ethical approval was obtained from..."
                ]
            ),
            
            WritingSectionType.RESULTS: WritingGuideline(
                section_type=WritingSectionType.RESULTS,
                purpose="Present findings objectively without interpretation",
                structure=[
                    "Descriptive statistics",
                    "Main findings",
                    "Secondary analyses",
                    "Tables and figures",
                    "Statistical results"
                ],
                key_elements=[
                    "Objective presentation",
                    "Clear statistical reporting",
                    "Appropriate tables/figures",
                    "Logical organization",
                    "No interpretation"
                ],
                word_count_range=(800, 1500),
                common_mistakes=[
                    "Including interpretation",
                    "Poor table/figure integration",
                    "Inadequate statistical reporting",
                    "Repetition between text and tables",
                    "Missing effect sizes"
                ],
                best_practices=[
                    "Report statistics completely",
                    "Use tables and figures effectively",
                    "Follow statistical reporting guidelines",
                    "Organize logically",
                    "Be objective and factual"
                ],
                example_phrases=[
                    "The results showed that...",
                    "As shown in Table X...",
                    "A significant difference was found...",
                    "The analysis revealed...",
                    "No significant relationship was observed..."
                ]
            ),
            
            WritingSectionType.DISCUSSION: WritingGuideline(
                section_type=WritingSectionType.DISCUSSION,
                purpose="Interpret findings, discuss implications, and acknowledge limitations",
                structure=[
                    "Summary of key findings",
                    "Interpretation of results",
                    "Comparison with literature",
                    "Implications",
                    "Limitations",
                    "Future directions"
                ],
                key_elements=[
                    "Clear interpretation",
                    "Literature integration",
                    "Practical implications",
                    "Honest limitations",
                    "Future research suggestions"
                ],
                word_count_range=(1200, 2000),
                common_mistakes=[
                    "Over-interpreting results",
                    "Ignoring contradictory findings",
                    "Insufficient literature integration",
                    "Missing limitations",
                    "Weak practical implications"
                ],
                best_practices=[
                    "Start with key findings",
                    "Integrate with existing literature",
                    "Discuss practical implications",
                    "Acknowledge limitations honestly",
                    "Suggest specific future research"
                ],
                example_phrases=[
                    "These findings suggest that...",
                    "This result is consistent with...",
                    "The practical implications of this study include...",
                    "A limitation of this study is...",
                    "Future research should investigate..."
                ]
            )
        }
    
    def _initialize_style_templates(self) -> dict[WritingStyle, dict[str, Any]]:
        """初始化写作风格模板"""
        return {
            WritingStyle.JOURNAL_ARTICLE: {
                "tone": "formal and objective",
                "person": "third person",
                "tense": "past tense for methods and results, present for general statements",
                "sentence_structure": "varied, but generally complex",
                "paragraph_length": "6-8 sentences",
                "citation_density": "high",
                "technical_language": "appropriate for field"
            },
            
            WritingStyle.CONFERENCE_PAPER: {
                "tone": "formal but accessible",
                "person": "third person, occasional first person plural",
                "tense": "mixed, present for contributions",
                "sentence_structure": "clear and direct",
                "paragraph_length": "4-6 sentences",
                "citation_density": "moderate to high",
                "technical_language": "accessible to broader audience"
            },
            
            WritingStyle.THESIS_DISSERTATION: {
                "tone": "formal and comprehensive",
                "person": "third person primarily",
                "tense": "past tense for research, present for general knowledge",
                "sentence_structure": "complex and detailed",
                "paragraph_length": "8-12 sentences",
                "citation_density": "very high",
                "technical_language": "detailed and precise"
            }
        }
    
    def _initialize_citation_formatters(self) -> dict[CitationStyle, dict[str, str]]:
        """初始化引用格式"""
        return {
            CitationStyle.APA: {
                "in_text_single": "({author}, {year})",
                "in_text_multiple": "({author1}, {year1}; {author2}, {year2})",
                "reference_journal": "{authors} ({year}). {title}. {journal}, {volume}({issue}), {pages}.",
                "reference_book": "{authors} ({year}). {title}. {publisher}."
            },
            
            CitationStyle.IEEE: {
                "in_text_single": "[{number}]",
                "in_text_multiple": "[{numbers}]",
                "reference_journal": "[{number}] {authors}, \"{title},\" {journal}, vol. {volume}, no. {issue}, pp. {pages}, {year}.",
                "reference_book": "[{number}] {authors}, {title}. {publisher}, {year}."
            },
            
            CitationStyle.MLA: {
                "in_text_single": "({author} {page})",
                "in_text_multiple": "({author1} {page1}; {author2} {page2})",
                "reference_journal": "{authors}. \"{title}.\" {journal}, vol. {volume}, no. {issue}, {year}, pp. {pages}.",
                "reference_book": "{authors}. {title}. {publisher}, {year}."
            }
        }
    
    async def analyze_writing_section(self, section: WritingSection, 
                                    writing_style: WritingStyle = WritingStyle.JOURNAL_ARTICLE) -> WritingFeedback:
        """分析写作章节"""
        try:
            logger.info(f"Analyzing {section.section_type} section")
            
            # 获取该章节的指导原则
            section_type = WritingSectionType(section.section_type.lower())
            guideline = self.writing_guidelines.get(section_type)
            
            if not guideline:
                logger.warning(f"No guideline found for section type: {section.section_type}")
                return self._create_default_feedback(section)
            
            # 分析各个方面
            grammar_issues = await self._analyze_grammar(section.content)
            style_issues = await self._analyze_style(section.content, writing_style)
            structure_feedback = await self._analyze_structure(section.content, guideline)
            clarity_score = await self._calculate_clarity_score(section.content)
            coherence_score = await self._calculate_coherence_score(section.content)
            academic_tone_score = await self._calculate_academic_tone_score(section.content)
            
            # 识别优点和缺点
            strengths = await self._identify_strengths(section, guideline)
            weaknesses = await self._identify_weaknesses(section, guideline)
            suggestions = await self._generate_suggestions(section, guideline, weaknesses)
            
            # 计算总体分数
            overall_score = (clarity_score + coherence_score + academic_tone_score) / 3
            
            feedback = WritingFeedback(
                section_type=section_type,
                overall_score=overall_score,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions,
                grammar_issues=grammar_issues,
                style_issues=style_issues,
                structure_feedback=structure_feedback,
                clarity_score=clarity_score,
                coherence_score=coherence_score,
                academic_tone_score=academic_tone_score
            )
            
            logger.info(f"Writing analysis completed with overall score: {overall_score:.2f}")
            return feedback
            
        except Exception as e:
            logger.error(f"Error analyzing writing section: {e}")
            return self._create_default_feedback(section)
    
    def _create_default_feedback(self, section: WritingSection) -> WritingFeedback:
        """创建默认反馈"""
        return WritingFeedback(
            section_type=WritingSectionType.INTRODUCTION,  # Default
            overall_score=0.5,
            strengths=["Content provided"],
            weaknesses=["Unable to analyze due to error"],
            suggestions=["Please check section format and try again"],
            grammar_issues=[],
            style_issues=[],
            structure_feedback="Unable to analyze structure",
            clarity_score=0.5,
            coherence_score=0.5,
            academic_tone_score=0.5
        )
    
    async def _analyze_grammar(self, content: str) -> list[str]:
        """分析语法问题"""
        issues = []
        
        # 简化的语法检查
        sentences = content.split('.')
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 检查常见语法问题
            if sentence and not sentence[0].isupper():
                issues.append(f"Sentence {i+1}: Should start with capital letter")
            
            if sentence.count('(') != sentence.count(')'):
                issues.append(f"Sentence {i+1}: Unmatched parentheses")
            
            # 检查过长句子
            if len(sentence.split()) > 30:
                issues.append(f"Sentence {i+1}: Consider breaking into shorter sentences")
            
            # 检查被动语态过多
            passive_indicators = ['was', 'were', 'been', 'being']
            passive_count = sum(1 for word in passive_indicators if word in sentence.lower())
            if passive_count > 2:
                issues.append(f"Sentence {i+1}: Consider using more active voice")
        
        return issues[:10]  # 限制问题数量
    
    async def _analyze_style(self, content: str, writing_style: WritingStyle) -> list[str]:
        """分析写作风格问题"""
        issues = []
        style_template = self.style_templates.get(writing_style, {})
        
        # 检查人称使用
        first_person_words = ['I', 'we', 'our', 'my']
        first_person_count = sum(content.lower().count(word.lower()) for word in first_person_words)
        
        if writing_style == WritingStyle.JOURNAL_ARTICLE and first_person_count > 5:
            issues.append("Excessive use of first person - consider third person perspective")
        
        # 检查非正式语言
        informal_words = ['really', 'very', 'quite', 'pretty', 'kind of', 'sort of']
        for word in informal_words:
            if word in content.lower():
                issues.append(f"Consider replacing informal word '{word}' with more academic language")
        
        # 检查缩写
        contractions = ["don't", "can't", "won't", "isn't", "aren't", "wasn't", "weren't"]
        for contraction in contractions:
            if contraction in content.lower():
                issues.append(f"Avoid contractions like '{contraction}' in academic writing")
        
        # 检查句子长度变化
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if sentences:
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            
            if avg_length < 10:
                issues.append("Sentences are quite short - consider combining some for better flow")
            elif avg_length > 25:
                issues.append("Sentences are quite long - consider breaking some down for clarity")
        
        return issues[:8]  # 限制问题数量
    
    async def _analyze_structure(self, content: str, guideline: WritingGuideline) -> str:
        """分析结构"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        feedback_parts = []
        
        # 检查段落数量
        if len(paragraphs) < 3:
            feedback_parts.append("Consider adding more paragraphs to develop ideas fully")
        elif len(paragraphs) > 8:
            feedback_parts.append("Consider consolidating some paragraphs for better flow")
        
        # 检查段落长度
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        if paragraph_lengths:
            avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths)
            
            if avg_paragraph_length < 50:
                feedback_parts.append("Paragraphs are quite short - consider developing ideas more fully")
            elif avg_paragraph_length > 200:
                feedback_parts.append("Paragraphs are quite long - consider breaking them down")
        
        # 检查结构元素
        structure_elements_found = 0
        for element in guideline.structure:
            # 简化的结构检查
            if any(keyword in content.lower() for keyword in element.lower().split()):
                structure_elements_found += 1
        
        structure_completeness = structure_elements_found / len(guideline.structure)
        if structure_completeness < 0.5:
            feedback_parts.append(f"Missing key structural elements. Consider including: {', '.join(guideline.structure)}")
        
        return "; ".join(feedback_parts) if feedback_parts else "Structure appears well-organized"
    
    async def _calculate_clarity_score(self, content: str) -> float:
        """计算清晰度分数"""
        score = 1.0
        
        # 检查句子长度
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_sentence_length > 25:
                score -= 0.2
            elif avg_sentence_length < 8:
                score -= 0.1
        
        # 检查复杂词汇密度
        words = content.split()
        complex_words = [w for w in words if len(w) > 8]
        complex_ratio = len(complex_words) / len(words) if words else 0
        
        if complex_ratio > 0.3:
            score -= 0.2
        elif complex_ratio < 0.1:
            score -= 0.1
        
        # 检查连接词使用
        transition_words = ['however', 'therefore', 'furthermore', 'moreover', 'consequently', 'nevertheless']
        transition_count = sum(1 for word in transition_words if word in content.lower())
        
        if transition_count < len(sentences) * 0.1:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    async def _calculate_coherence_score(self, content: str) -> float:
        """计算连贯性分数"""
        score = 1.0
        
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # 检查段落间连接
        if len(paragraphs) > 1:
            transitions_between_paragraphs = 0
            transition_indicators = ['first', 'second', 'next', 'finally', 'in addition', 'furthermore', 'however', 'therefore']
            
            for paragraph in paragraphs[1:]:  # Skip first paragraph
                first_sentence = paragraph.split('.')[0].lower()
                if any(indicator in first_sentence for indicator in transition_indicators):
                    transitions_between_paragraphs += 1
            
            transition_ratio = transitions_between_paragraphs / (len(paragraphs) - 1)
            if transition_ratio < 0.3:
                score -= 0.2
        
        # 检查主题一致性（简化版）
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if len(sentences) > 3:
            # 简单的关键词重复检查
            all_words = content.lower().split()
            word_freq = {}
            for word in all_words:
                if len(word) > 4:  # 只考虑较长的词
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # 检查是否有重复的关键概念
            repeated_concepts = sum(1 for freq in word_freq.values() if freq > 2)
            if repeated_concepts < 3:
                score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    async def _calculate_academic_tone_score(self, content: str) -> float:
        """计算学术语调分数"""
        score = 1.0
        
        # 检查学术词汇使用
        academic_words = [
            'research', 'study', 'analysis', 'findings', 'results', 'methodology',
            'significant', 'demonstrate', 'indicate', 'suggest', 'examine', 'investigate'
        ]
        
        academic_word_count = sum(1 for word in academic_words if word in content.lower())
        word_count = len(content.split())
        academic_ratio = academic_word_count / word_count if word_count > 0 else 0
        
        if academic_ratio < 0.02:
            score -= 0.2
        
        # 检查非正式语言
        informal_indicators = ['really', 'very', 'quite', 'pretty', 'kind of', 'sort of', 'a lot of']
        informal_count = sum(1 for word in informal_indicators if word in content.lower())
        
        if informal_count > 3:
            score -= 0.3
        
        # 检查客观性
        subjective_words = ['I think', 'I believe', 'in my opinion', 'obviously', 'clearly']
        subjective_count = sum(1 for phrase in subjective_words if phrase in content.lower())
        
        if subjective_count > 2:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    async def _identify_strengths(self, section: WritingSection, guideline: WritingGuideline) -> list[str]:
        """识别写作优点"""
        strengths = []
        
        # 检查字数是否合适
        word_count = section.word_count
        min_words, max_words = guideline.word_count_range
        
        if min_words <= word_count <= max_words:
            strengths.append(f"Appropriate word count ({word_count} words)")
        
        # 检查是否包含关键元素
        content_lower = section.content.lower()
        elements_found = 0
        
        for element in guideline.key_elements:
            # 简化的关键元素检查
            element_keywords = element.lower().split()
            if any(keyword in content_lower for keyword in element_keywords):
                elements_found += 1
        
        if elements_found >= len(guideline.key_elements) * 0.6:
            strengths.append("Includes most required elements")
        
        # 检查段落结构
        paragraphs = [p.strip() for p in section.content.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            strengths.append("Well-structured with multiple paragraphs")
        
        # 检查学术语言使用
        academic_indicators = ['research', 'study', 'analysis', 'findings', 'methodology']
        academic_count = sum(1 for word in academic_indicators if word in content_lower)
        
        if academic_count >= 3:
            strengths.append("Uses appropriate academic language")
        
        return strengths if strengths else ["Content is provided and readable"]
    
    async def _identify_weaknesses(self, section: WritingSection, guideline: WritingGuideline) -> list[str]:
        """识别写作弱点"""
        weaknesses = []
        
        # 检查字数
        word_count = section.word_count
        min_words, max_words = guideline.word_count_range
        
        if word_count < min_words:
            weaknesses.append(f"Too short ({word_count} words, recommended: {min_words}-{max_words})")
        elif word_count > max_words * 1.2:
            weaknesses.append(f"Too long ({word_count} words, recommended: {min_words}-{max_words})")
        
        # 检查常见错误
        content_lower = section.content.lower()
        
        for mistake in guideline.common_mistakes:
            # 简化的错误检查
            if "word limit" in mistake.lower() and word_count > max_words:
                weaknesses.append("Exceeds recommended word limit")
            elif "citations" in mistake.lower() and guideline.section_type == WritingSectionType.ABSTRACT:
                if any(indicator in content_lower for indicator in ['et al', '(', ')']):
                    weaknesses.append("Abstract should not contain citations")
        
        # 检查结构完整性
        structure_elements_found = 0
        for element in guideline.structure:
            element_keywords = element.lower().split()
            if any(keyword in content_lower for keyword in element_keywords):
                structure_elements_found += 1
        
        if structure_elements_found < len(guideline.structure) * 0.5:
            weaknesses.append("Missing key structural elements")
        
        return weaknesses
    
    async def _generate_suggestions(self, section: WritingSection, 
                                  guideline: WritingGuideline, 
                                  weaknesses: list[str]) -> list[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于弱点生成建议
        for weakness in weaknesses:
            if "too short" in weakness.lower():
                suggestions.append("Expand on key points and provide more detailed explanations")
            elif "too long" in weakness.lower():
                suggestions.append("Consider condensing content and removing redundant information")
            elif "missing" in weakness.lower():
                suggestions.append(f"Include the following elements: {', '.join(guideline.structure)}")
        
        # 基于最佳实践生成建议
        for practice in guideline.best_practices[:3]:  # 限制建议数量
            suggestions.append(f"Best practice: {practice}")
        
        # 添加示例短语建议
        if guideline.example_phrases:
            suggestions.append(f"Consider using phrases like: '{guideline.example_phrases[0]}'")
        
        return suggestions[:5]  # 限制建议数量
    
    async def generate_writing_template(self, section_type: WritingSectionType, 
                                      writing_style: WritingStyle = WritingStyle.JOURNAL_ARTICLE) -> str:
        """生成写作模板"""
        try:
            logger.info(f"Generating template for {section_type.value}")
            
            guideline = self.writing_guidelines.get(section_type)
            if not guideline:
                return f"Template not available for {section_type.value}"
            
            style_info = self.style_templates.get(writing_style, {})
            
            template_parts = [
                f"# {section_type.value.replace('_', ' ').title()} Template",
                "",
                f"**Purpose**: {guideline.purpose}",
                f"**Word Count**: {guideline.word_count_range[0]}-{guideline.word_count_range[1]} words",
                f"**Writing Style**: {style_info.get('tone', 'Academic formal')}",
                "",
                "## Structure",
                ""
            ]
            
            # 添加结构指导
            for i, element in enumerate(guideline.structure, 1):
                template_parts.extend([
                    f"### {i}. {element}",
                    f"[Write about {element.lower()} here. Consider including...]",
                    ""
                ])
            
            # 添加关键要素
            template_parts.extend([
                "## Key Elements to Include",
                ""
            ])
            
            for element in guideline.key_elements:
                template_parts.append(f"- {element}")
            
            # 添加示例短语
            if guideline.example_phrases:
                template_parts.extend([
                    "",
                    "## Useful Phrases",
                    ""
                ])
                
                for phrase in guideline.example_phrases:
                    template_parts.append(f"- {phrase}")
            
            # 添加最佳实践
            template_parts.extend([
                "",
                "## Best Practices",
                ""
            ])
            
            for practice in guideline.best_practices:
                template_parts.append(f"- {practice}")
            
            template = "\n".join(template_parts)
            
            logger.info("Writing template generated successfully")
            return template
            
        except Exception as e:
            logger.error(f"Error generating writing template: {e}")
            return "Error generating template"
    
    async def format_citations(self, citations: list[Citation], 
                             citation_style: CitationStyle = CitationStyle.APA) -> dict[str, list[str]]:
        """格式化引用"""
        try:
            logger.info(f"Formatting {len(citations)} citations in {citation_style.value} style")
            
            formatter = self.citation_formatters.get(citation_style, {})
            if not formatter:
                return {"error": ["Citation style not supported"]}
            
            in_text_citations = []
            reference_list = []
            
            for i, citation in enumerate(citations, 1):
                # 生成文内引用
                if citation_style == CitationStyle.APA:
                    authors_str = citation.authors[0].split(',')[0] if citation.authors else "Unknown"
                    if len(citation.authors) > 1:
                        authors_str += " et al." if len(citation.authors) > 2 else f" & {citation.authors[1].split(',')[0]}"
                    
                    in_text = f"({authors_str}, {citation.year})"
                    in_text_citations.append(in_text)
                
                elif citation_style == CitationStyle.IEEE:
                    in_text_citations.append(f"[{i}]")
                
                # 生成参考文献条目
                authors_formatted = self._format_authors(citation.authors, citation_style)
                
                if citation.citation_type == "journal":
                    reference = formatter.get("reference_journal", "").format(
                        authors=authors_formatted,
                        year=citation.year,
                        title=citation.title,
                        journal=citation.venue,
                        volume="X",  # 简化处理
                        issue="X",
                        pages=citation.pages or "XX-XX"
                    )
                else:
                    reference = formatter.get("reference_book", "").format(
                        authors=authors_formatted,
                        year=citation.year,
                        title=citation.title,
                        publisher=citation.venue
                    )
                
                if citation_style == CitationStyle.IEEE:
                    reference = f"[{i}] {reference}"
                
                reference_list.append(reference)
            
            result = {
                "in_text_citations": in_text_citations,
                "reference_list": reference_list
            }
            
            logger.info("Citations formatted successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error formatting citations: {e}")
            return {"error": ["Error formatting citations"]}
    
    def _format_authors(self, authors: list[str], citation_style: CitationStyle) -> str:
        """格式化作者名单"""
        if not authors:
            return "Unknown Author"
        
        if citation_style == CitationStyle.APA:
            if len(authors) == 1:
                return authors[0]
            elif len(authors) == 2:
                return f"{authors[0]} & {authors[1]}"
            else:
                return f"{authors[0]} et al."
        
        elif citation_style == CitationStyle.IEEE:
            if len(authors) <= 3:
                return ", ".join(authors)
            else:
                return f"{authors[0]} et al."
        
        else:
            return ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
    
    async def generate_writing_report(self, feedback: WritingFeedback) -> str:
        """生成写作报告"""
        try:
            logger.info("Generating writing feedback report")
            
            report_sections = [
                "# Writing Analysis Report",
                "",
                f"**Section Type**: {feedback.section_type.value.replace('_', ' ').title()}",
                f"**Overall Score**: {feedback.overall_score:.2f}/1.00",
                "",
                "## Score Breakdown",
                f"- **Clarity**: {feedback.clarity_score:.2f}/1.00",
                f"- **Coherence**: {feedback.coherence_score:.2f}/1.00", 
                f"- **Academic Tone**: {feedback.academic_tone_score:.2f}/1.00",
                "",
                "## Strengths",
                ""
            ]
            
            for strength in feedback.strengths:
                report_sections.append(f"✅ {strength}")
            
            report_sections.extend([
                "",
                "## Areas for Improvement",
                ""
            ])
            
            for weakness in feedback.weaknesses:
                report_sections.append(f"⚠️ {weakness}")
            
            if feedback.grammar_issues:
                report_sections.extend([
                    "",
                    "## Grammar Issues",
                    ""
                ])
                
                for issue in feedback.grammar_issues:
                    report_sections.append(f"📝 {issue}")
            
            if feedback.style_issues:
                report_sections.extend([
                    "",
                    "## Style Issues", 
                    ""
                ])
                
                for issue in feedback.style_issues:
                    report_sections.append(f"🎨 {issue}")
            
            report_sections.extend([
                "",
                "## Structure Feedback",
                f"{feedback.structure_feedback}",
                "",
                "## Suggestions for Improvement",
                ""
            ])
            
            for suggestion in feedback.suggestions:
                report_sections.append(f"💡 {suggestion}")
            
            report = "\n".join(report_sections)
            
            logger.info("Writing report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating writing report: {e}")
            return "Error generating writing report"