"""@Time: 2025-08-03
@Author: DAIP-LIVE
@File: knowledge_visualization_engine.py
@Description: V0.3.4 知识可视化引擎 - 交互式知识图谱和可视化组件
"""

import asyncio
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

# 延迟加载的可视化库
_matplotlib_plt = None
_matplotlib_mdates = None
_matplotlib_figure = None
_seaborn = None
_plotly_go = None
_plotly_px = None
_plotly_subplots = None
_pandas = None
_numpy = None
_networkx = None

def _get_networkx():
    global _networkx
    if _networkx is None:
        try:
            import networkx as nx
            _networkx = nx
        except ImportError:
            raise ImportError("networkx is required for knowledge visualization. Please install it with 'pip install networkx'")
    return _networkx

def _get_plotly_go():
    global _plotly_go
    if _plotly_go is None:
        try:
            import plotly.graph_objects as go
            _plotly_go = go
        except ImportError:
            raise ImportError("plotly is required for interactive visualizations. Please install it with 'pip install plotly'")
    return _plotly_go

def _get_plotly_px():
    global _plotly_px
    if _plotly_px is None:
        try:
            import plotly.express as px
            _plotly_px = px
        except ImportError:
            raise ImportError("plotly is required for interactive visualizations. Please install it with 'pip install plotly'")
    return _plotly_px

def _get_matplotlib_plt():
    global _matplotlib_plt
    if _matplotlib_plt is None:
        try:
            import matplotlib.pyplot as plt
            _matplotlib_plt = plt
        except ImportError:
            raise ImportError("matplotlib.pyplot is required for visualization")
    return _matplotlib_plt

def _get_matplotlib_mdates():
    global _matplotlib_mdates
    if _matplotlib_mdates is None:
        try:
            import matplotlib.dates as mdates
            _matplotlib_mdates = mdates
        except ImportError:
            raise ImportError("matplotlib.dates is required for visualization")
    return _matplotlib_mdates

def _get_matplotlib_figure():
    global _matplotlib_figure
    if _matplotlib_figure is None:
        try:
            import matplotlib.figure as figure
            _matplotlib_figure = figure
        except ImportError:
            raise ImportError("matplotlib.figure is required for visualization")
    return _matplotlib_figure

def _get_seaborn():
    global _seaborn
    if _seaborn is None:
        try:
            import seaborn as sns
            _seaborn = sns
        except ImportError:
            raise ImportError("seaborn is required for visualization. Please install it with 'pip install seaborn'")
    return _seaborn

def _get_pandas():
    global _pandas
    if _pandas is None:
        try:
            import pandas as pd
            _pandas = pd
        except ImportError:
            raise ImportError("pandas is required for data processing. Please install it with 'pip install pandas'")
    return _pandas

def _get_numpy():
    global _numpy
    if _numpy is None:
        try:
            import numpy as np
            _numpy = np
        except ImportError:
            raise ImportError("numpy is required for numerical computations. Please install it with 'pip install numpy'")
    return _numpy