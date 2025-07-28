#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流状态卡片组件

专门用于显示工作流执行状态的可视化卡片
支持进度显示、状态图标和实时更新
"""

from lona.html.widget import Widget
from lona.html import HTML, Div, Span, P, H4
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class WorkflowStat(Widget):
    pass
