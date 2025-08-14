#!/usr/bin/env python3
"""富文本渲染器

支持Markdown、代码高亮、工作流状态等多种内容格式的渲染
"""

import logging
from typing import Any, Dict, Optional

from lona.html import H1, H2, H3, HTML, Br, Code, Div, Em, P, Pre, Span, Strong

logger = logging.getLogger(__name__)


class RichTextRenderer:
    """富文本渲染器"""

    def __init__(self):
        # Markdown样式映射
        self.markdown_patterns = {
            r'\*\*(.*?)\*\*': lambda m: Strong(m.group(1)),  # 粗体
            r'\*(.*?)\*': lambda m: Em(m.group(1)),          # 斜体
            r'`(.*?)`': lambda m: Code(m.group(1)),          # 行内代码
            r'^# (.*?)$': lambda m: H1(m.group(1)),          # 一级标题
            r'^## (.*?)$': lambda m: H2(m.group(1)),         # 二级标题
            r'^### (.*?)$': lambda m: H3(m.group(1)),        # 三级标题
        }

        # 代码语言映射（用于语法高亮）
        self.code_languages = {
            'python': 'language-python',
            'javascript': 'language-javascript',
            'java': 'language-java',
            'cpp': 'language-cpp',
            'html': 'language-html',
            'css': 'language-css',
            'json': 'language-json',
            'yaml': 'language-yaml',
            'sql': 'language-sql'
        }

    def render(self, content: Any, content_type: str = "text") -> HTML:
        """渲染内容
        
        Args:
            content: 要渲染的内容
            content_type: 内容类型 (text, markdown, code, agent_output, workflow_status)
        
        Returns:
            HTML: 渲染后的HTML元素

        """
        try:
            if content_type == "text":
                return self._render_text(content)
            elif content_type == "markdown":
                return self._render_markdown(content)
            elif content_type == "code":
                return self._render_code(content)
            elif content_type == "agent_output":
                return self._render_agent_output(content)
            elif content_type == "workflow_status":
                return self._render_workflow_status(content)
            else:
                return self._render_text(str(content))

        except Exception as e:
            logger.error(f"渲染内容失败 ({content_type}): {e}")
            return P(str(content))

    def _render_text(self, text: str) -> HTML:
        """渲染普通文本"""
        if not text:
            return P("")

        # 处理换行
        lines = str(text).split('\\n')
        elements = []

        for i, line in enumerate(lines):
            if line.strip():
                # 检查是否是列表项
                if line.strip().startswith('• ') or line.strip().startswith('- '):
                    elements.append(
                        Div(
                            Span("• ", _class="bullet-point"),
                            Span(line.strip()[2:]),
                            _class="list-item"
                        )
                    )
                else:
                    elements.append(P(line))
            else:
                elements.append(Br())

        return Div(*elements, _class="text-content")

    def _render_markdown(self, markdown_text: str) -> HTML:
        """渲染Markdown文本"""
        if not markdown_text:
            return P("")

        lines = str(markdown_text).split('\\n')
        elements = []
        in_code_block = False
        code_lines = []
        code_language = ""

        for line in lines:
            # 处理代码块
            if line.strip().startswith('```'):
                if not in_code_block:
                    # 开始代码块
                    in_code_block = True
                    code_language = line.strip()[3:].strip()
                    code_lines = []
                else:
                    # 结束代码块
                    in_code_block = False
                    code_content = '\\n'.join(code_lines)
                    elements.append(self._render_code_block(code_content, code_language))
                    code_lines = []
                    code_language = ""
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            # 处理普通Markdown
            rendered_line = self._process_markdown_line(line)
            if rendered_line:
                elements.append(rendered_line)
            else:
                elements.append(Br())

        return Div(*elements, _class="markdown-content")

    def _process_markdown_line(self, line: str) -> Optional[HTML]:
        """处理单行Markdown"""
        if not line.strip():
            return None

        # 检查标题
        if line.startswith('### '):
            return H3(line[4:])
        elif line.startswith('## '):
            return H2(line[3:])
        elif line.startswith('# '):
            return H1(line[2:])

        # 检查列表
        if line.strip().startswith('• ') or line.strip().startswith('- '):
            return Div(
                Span("• ", _class="bullet-point"),
                self._process_inline_markdown(line.strip()[2:]),
                _class="list-item"
            )

        # 处理普通段落
        return P(self._process_inline_markdown(line))

    def _process_inline_markdown(self, text: str) -> HTML:
        """处理行内Markdown元素"""
        elements = []
        current_text = text

        # 处理粗体 **text**
        while '**' in current_text:
            start = current_text.find('**')
            if start == -1:
                break
            end = current_text.find('**', start + 2)
            if end == -1:
                break

            # 添加前面的文本
            if start > 0:
                elements.append(current_text[:start])

            # 添加粗体文本
            bold_text = current_text[start + 2:end]
            elements.append(Strong(bold_text))

            # 继续处理剩余文本
            current_text = current_text[end + 2:]

        # 处理斜体 *text*
        while '*' in current_text and '**' not in current_text:
            start = current_text.find('*')
            if start == -1:
                break
            end = current_text.find('*', start + 1)
            if end == -1:
                break

            # 添加前面的文本
            if start > 0:
                elements.append(current_text[:start])

            # 添加斜体文本
            italic_text = current_text[start + 1:end]
            elements.append(Em(italic_text))

            # 继续处理剩余文本
            current_text = current_text[end + 1:]

        # 处理行内代码 `code`
        while '`' in current_text:
            start = current_text.find('`')
            if start == -1:
                break
            end = current_text.find('`', start + 1)
            if end == -1:
                break

            # 添加前面的文本
            if start > 0:
                elements.append(current_text[:start])

            # 添加代码文本
            code_text = current_text[start + 1:end]
            elements.append(Code(code_text))

            # 继续处理剩余文本
            current_text = current_text[end + 1:]

        # 添加剩余文本
        if current_text:
            elements.append(current_text)

        return Span(*elements) if len(elements) > 1 else (elements[0] if elements else "")

    def _render_code(self, code_content: str) -> HTML:
        """渲染代码内容"""
        if not code_content:
            return Pre("")

        # 检查是否是代码块格式
        if code_content.startswith('```') and code_content.endswith('```'):
            lines = code_content.split('\\n')
            language = lines[0][3:].strip() if len(lines) > 0 else ""
            code_lines = lines[1:-1] if len(lines) > 2 else []
            code_text = '\\n'.join(code_lines)
            return self._render_code_block(code_text, language)
        else:
            # 行内代码
            return Code(code_content, _class="inline-code")

    def _render_code_block(self, code: str, language: str = "") -> HTML:
        """渲染代码块"""
        css_class = "code-block"
        if language and language in self.code_languages:
            css_class += f" {self.code_languages[language]}"

        return Pre(
            Code(code, _class=css_class),
            _class="code-container"
        )

    def _render_agent_output(self, content: str) -> HTML:
        """渲染代理输出"""
        if not content:
            return P("")

        # 代理输出通常包含结构化内容
        # 检查是否包含特殊标记
        if "**分析结果**" in content or "**结论**" in content:
            return self._render_structured_analysis(content)
        elif content.startswith("```") and content.endswith("```"):
            return self._render_code(content)
        else:
            return self._render_markdown(content)

    def _render_structured_analysis(self, content: str) -> HTML:
        """渲染结构化分析内容"""
        sections = []
        current_section = []
        current_title = None

        lines = content.split('\\n')

        for line in lines:
            if line.strip().startswith('**') and line.strip().endswith('**'):
                # 新的章节标题
                if current_section and current_title:
                    sections.append((current_title, current_section))

                current_title = line.strip()[2:-2]  # 移除 ** 标记
                current_section = []
            else:
                if line.strip():
                    current_section.append(line)

        # 添加最后一个章节
        if current_section and current_title:
            sections.append((current_title, current_section))

        # 渲染章节
        elements = []
        for title, section_lines in sections:
            elements.append(
                Div(
                    H3(title, _class="analysis-section-title"),
                    Div(
                        *[P(line) for line in section_lines if line.strip()],
                        _class="analysis-section-content"
                    ),
                    _class="analysis-section"
                )
            )

        return Div(*elements, _class="structured-analysis")

    def _render_workflow_status(self, status_data: Dict[str, Any]) -> HTML:
        """渲染工作流状态"""
        if not isinstance(status_data, dict):
            return P(str(status_data))

        elements = []

        # 工作流基本信息
        workflow_id = status_data.get("workflow_id", "Unknown")
        status = status_data.get("status", "unknown")
        current_step = status_data.get("current_step", "")
        progress = status_data.get("progress", 0)

        # 状态图标映射
        status_icons = {
            "preparing": "🔄",
            "running": "⚡",
            "completed": "✅",
            "failed": "❌",
            "paused": "⏸️"
        }

        icon = status_icons.get(status, "🔄")

        # 主要状态信息
        elements.append(
            Div(
                Span(f"{icon} 工作流: {workflow_id}", _class="workflow-title"),
                Span(f"状态: {status}", _class=f"workflow-status status-{status}"),
                _class="workflow-header"
            )
        )

        # 当前步骤
        if current_step:
            elements.append(
                P(f"当前步骤: {current_step}", _class="workflow-step")
            )

        # 进度条
        if progress > 0:
            elements.append(
                Div(
                    Div(
                        style=f"width: {progress * 100}%; height: 100%; background: #2ecc71; border-radius: 2px;"
                    ),
                    P(f"进度: {progress * 100:.1f}%", _class="progress-text"),
                    _class="progress-bar",
                    style="width: 100%; height: 20px; background: #e9ecef; border-radius: 2px; position: relative; margin: 10px 0;"
                )
            )

        # 参与者信息
        participants = status_data.get("participants", [])
        if participants:
            participant_elements = [
                Span(f"👤 {participant}", _class="participant-tag")
                for participant in participants
            ]
            elements.append(
                Div(
                    P("参与者:", _class="participants-label"),
                    Div(*participant_elements, _class="participants-list"),
                    _class="workflow-participants"
                )
            )

        return Div(*elements, _class="workflow-status-card")

    def render_consensus_result(self, consensus_data: Dict[str, Any]) -> HTML:
        """渲染共识结果"""
        if not isinstance(consensus_data, dict):
            return P(str(consensus_data))

        result = consensus_data.get("result", "No consensus")
        confidence = consensus_data.get("confidence", 0)
        participants = consensus_data.get("participants", [])
        reasoning = consensus_data.get("reasoning", "")

        # 置信度颜色
        confidence_color = "red" if confidence < 0.5 else "orange" if confidence < 0.8 else "green"

        elements = [
            Div(
                Span("🎯 共识结果", _class="consensus-title"),
                Span(f"{confidence:.1%}", _class=f"confidence-score confidence-{confidence_color}"),
                _class="consensus-header"
            ),
            P(result, _class="consensus-result"),
        ]

        if reasoning:
            elements.append(
                Div(
                    P("推理过程:", _class="reasoning-label"),
                    P(reasoning, _class="reasoning-content"),
                    _class="consensus-reasoning"
                )
            )

        if participants:
            elements.append(
                Div(
                    P(f"参与者: {', '.join(participants)}", _class="consensus-participants"),
                    _class="consensus-meta"
                )
            )

        return Div(*elements, _class="consensus-result-card")


# 全局富文本渲染器实例
rich_text_renderer = RichTextRenderer()
