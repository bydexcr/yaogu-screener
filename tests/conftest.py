# -*- coding: utf-8 -*-
"""让测试能 import 仓库根的 strategy / web 包。"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
