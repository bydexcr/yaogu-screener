# -*- coding: utf-8 -*-
"""
web 子包：将 web/ 显式声明为常规包（而非命名空间包），
以便在 Chaquopy(Android) 环境下 `from web import stock_market` 与包内相对导入都稳定可用。
"""
