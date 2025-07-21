#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-21 14:40:00
@Author  : DAIP-LIVE Team
@File    : setup.py
@Description: Setup script for installing the DAIP-LIVE CLI
"""

from setuptools import setup, find_packages

setup(
    name="daip-mvp-project",
    version="0.1.0",
    description="DAIP-L.I.V.E. 智能协作平台，支持多AI角色协作与知识管理。",
    author="DAIP-LIVE Team",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10,<3.13",
    entry_points={
        "console_scripts": [
            "daip-cli=src.cli.main:app",
        ],
    },
)