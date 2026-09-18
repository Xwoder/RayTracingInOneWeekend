"""Interval 类的 pytest 测试。

运行方式（在项目根目录，用 .venv 的解释器）：
    .venv/bin/python -m pytest            # 跑全部测试
    .venv/bin/python -m pytest tests/test_interval.py -v   # 详细模式
    .venv/bin/python -m pytest -k "surrounds" -v           # 只跑名字含 surrounds 的
"""

import math

import pytest

from Interval import Interval


# ---------------------------------------------------------------------------
# 1) 用 fixture 准备可复用的测试对象（相当于把 setUp 抽出来）
# ---------------------------------------------------------------------------
@pytest.fixture
def normal_interval() -> Interval:
    """一个普通区间 [3, 10]。"""
    return Interval(3.0, 10.0)


# ---------------------------------------------------------------------------
# 2) 基本构造与属性
# ---------------------------------------------------------------------------
def test_default_is_empty():
    e = Interval()
    assert e == Interval.empty
    assert e.min == math.inf
    assert e.max == -math.inf
    # size = -inf - (+inf) = -inf
    assert e.size() == -math.inf


def test_normal_construction(normal_interval: Interval):
    assert normal_interval.min == 3.0
    assert normal_interval.max == 10.0
    assert normal_interval.size() == 7.0


# ---------------------------------------------------------------------------
# 3) parametrize：用多组参数批量测同一个逻辑，避免重复的 assert
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "x, expected",
    [
        (3.0, True),    # 闭区间含左端点
        (10.0, True),   # 闭区间含右端点
        (5.0, True),    # 区间内
        (2.0, False),   # 小于下界
        (11.0, False),  # 大于上界
    ],
)
def test_contains(normal_interval: Interval, x: float, expected: bool):
    assert normal_interval.contains(x) is expected


@pytest.mark.parametrize(
    "x, expected",
    [
        (5.0, True),    # 区间内
        (3.0, False),   # 不含左端点
        (10.0, False),  # 不含右端点
        (2.0, False),   # 小于下界
        (11.0, False),  # 大于上界
    ],
)
def test_surrounds(normal_interval: Interval, x: float, expected: bool):
    assert normal_interval.surrounds(x) is expected


# ---------------------------------------------------------------------------
# 4) 静态成员（empty / universe）
# ---------------------------------------------------------------------------
def test_static_members():
    assert Interval.empty.min == math.inf
    assert Interval.empty.max == -math.inf
    assert Interval.universe.min == -math.inf
    assert Interval.universe.max == math.inf
    assert Interval.universe.contains(0.0)
    assert Interval.universe.surrounds(0.0)
    assert Interval.universe.surrounds(-1e9)
    assert Interval.universe.surrounds(1e9)


# ---------------------------------------------------------------------------
# 5) 空区间的行为
# ---------------------------------------------------------------------------
def test_empty_contains_nothing():
    e = Interval()
    assert not e.contains(0.0)
    assert not e.surrounds(0.0)


# ---------------------------------------------------------------------------
# 6) __repr__ 可还原
# ---------------------------------------------------------------------------
def test_repr_roundtrip(normal_interval: Interval):
    assert eval(repr(normal_interval)) == normal_interval


# ---------------------------------------------------------------------------
# 7) 用 pytest.approx 处理浮点比较（更稳健）
# ---------------------------------------------------------------------------
def test_size_with_approx():
    i = Interval(2.1, 5.7)
    assert i.size() == pytest.approx(3.6)
