#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-21 14:35:00
@Author  : DAIP-LIVE Team
@File    : daip-cli.py
@Description: Standalone script to run the DAIP-LIVE CLI
"""

import sys
import os
from pathlib import Path

# Add project root to path to ensure imports work correctly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.cli.main import app

if __name__ == "__main__":
    app()