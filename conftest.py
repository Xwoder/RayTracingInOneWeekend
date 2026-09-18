"""项目根目录的 conftest.py。

作用：让 pytest 把项目根目录加入 sys.path，这样测试里
`from Interval import Interval` 才能找到模块（pytest 默认会把
conftest.py 所在目录加入 sys.path）。
"""
