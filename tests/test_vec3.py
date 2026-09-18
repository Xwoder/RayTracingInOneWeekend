"""Vec3 类的 pytest 测试（由 Vec3.py 原 __main__ 自测块迁移而来）。

运行：
    .venv/bin/python -m pytest tests/test_vec3.py -v
"""

import math

import pytest

from Vec3 import Vec3


@pytest.fixture
def v() -> Vec3:
    """向量 (1, 2, 3)。"""
    return Vec3(1, 2, 3)


@pytest.fixture
def w() -> Vec3:
    """向量 (4, 5, 6)。"""
    return Vec3(4, 5, 6)


# ---------------------------------------------------------------------------
# 构造 / 属性 / 类方法
# ---------------------------------------------------------------------------
def test_constructor_and_repr(v: Vec3):
    assert repr(v) == "Vec3(1, 2, 3)"


def test_properties(v: Vec3):
    assert (v.x, v.y, v.z) == (1, 2, 3)


def test_from_sequence():
    w = Vec3.from_sequence([4, 5, 6])
    assert w == Vec3(4, 5, 6)


def test_from_sequence_requires_three_values():
    with pytest.raises(ValueError):
        Vec3.from_sequence([1, 2])


def test_zero_and_one_classmethods():
    assert Vec3.zero() == Vec3(0, 0, 0)
    assert Vec3.one() == Vec3(1, 1, 1)


# ---------------------------------------------------------------------------
# 运算符
# ---------------------------------------------------------------------------
def test_neg(v: Vec3):
    assert -v == Vec3(-1, -2, -3)


def test_getitem(v: Vec3):
    assert (v[0], v[1], v[2]) == (1, 2, 3)


def test_getitem_out_of_range(v: Vec3):
    with pytest.raises(IndexError):
        _ = v[3]


def test_add(v: Vec3, w: Vec3):
    assert v + w == Vec3(5, 7, 9)


def test_sub(v: Vec3, w: Vec3):
    assert w - v == Vec3(3, 3, 3)


def test_mul_scalar(v: Vec3):
    assert v * 2 == Vec3(2, 4, 6)


def test_mul_vector(v: Vec3, w: Vec3):
    assert v * w == Vec3(4, 10, 18)


def test_rmul_scalar(v: Vec3):
    assert 3 * v == Vec3(3, 6, 9)


def test_truediv_scalar(v: Vec3):
    assert v / 2 == Vec3(0.5, 1.0, 1.5)


def test_truediv_vector(v: Vec3, w: Vec3):
    assert Vec3(2, 4, 6) / w == Vec3(0.5, 0.8, 1.0)


def test_eq(v: Vec3):
    assert v == Vec3(1, 2, 3)
    assert v != Vec3(0, 0, 0)
    assert v != "not a vec"


# ---------------------------------------------------------------------------
# 几何方法
# ---------------------------------------------------------------------------
def test_length_squared(v: Vec3):
    assert v.length_squared() == 14


@pytest.mark.parametrize(
    "vec, expected",
    [
        (Vec3(0, 0, 0), True),
        (Vec3(1e-9, 1e-9, 1e-9), True),
        (Vec3(1e-7, 0, 0), False),
    ],
)
def test_near_zero(vec: Vec3, expected: bool):
    assert vec.near_zero() is expected


def test_length(v: Vec3):
    assert v.length() == pytest.approx(math.sqrt(14))


def test_dot(v: Vec3, w: Vec3):
    assert v.dot(w) == 1 * 4 + 2 * 5 + 3 * 6


def test_cross(v: Vec3, w: Vec3):
    assert v.cross(w) == Vec3(2 * 6 - 3 * 5, 3 * 4 - 1 * 6, 1 * 5 - 2 * 4)


def test_unit_vector():
    assert Vec3(3, 0, 0).unit_vector() == Vec3(1, 0, 0)


def test_unit_vector_of_zero_raises():
    with pytest.raises(ZeroDivisionError):
        Vec3(0, 0, 0).unit_vector()


# ---------------------------------------------------------------------------
# 随机相关（检查范围/分布，不依赖固定种子）
# ---------------------------------------------------------------------------
def test_random_default_range():
    r = Vec3.random()
    assert 0.0 <= r.x < 1.0
    assert 0.0 <= r.y < 1.0
    assert 0.0 <= r.z < 1.0


def test_random_custom_range():
    r = Vec3.random(-2.0, 3.0)
    assert -2.0 <= r.x < 3.0
    assert -2.0 <= r.y < 3.0
    assert -2.0 <= r.z < 3.0


def test_random_is_actually_random():
    samples = [Vec3.random() for _ in range(8)]
    assert len({(s.x, s.y, s.z) for s in samples}) == 8


def test_random_unit_vector():
    for _ in range(100):
        u = Vec3.random_unit_vector()
        assert -1.0 <= u.x <= 1.0
        assert -1.0 <= u.y <= 1.0
        assert -1.0 <= u.z <= 1.0
        assert u.length() == pytest.approx(1.0, abs=1e-12)


def test_random_unit_vector_never_zero():
    directions = [Vec3.random_unit_vector() for _ in range(50)]
    assert all(d.length_squared() > 1e-160 for d in directions)


def test_random_on_hemisphere():
    n = Vec3(0, 0, 1)
    for _ in range(200):
        d = Vec3.random_on_hemisphere(n)
        assert d.dot(n) > 0.0
        assert d.length() == pytest.approx(1.0, abs=1e-12)
        # 取反法线应落在另一侧半球
        assert Vec3.random_on_hemisphere(-n).dot(-n) > 0.0


# ---------------------------------------------------------------------------
# reflect / refract 静态方法
# ---------------------------------------------------------------------------
def test_reflect():
    # 竖直入射经水平面法线反射
    assert Vec3.reflect(Vec3(0, -1, 0), Vec3(0, 1, 0)) == Vec3(0, 1, 0)
    # 斜入射
    assert Vec3.reflect(Vec3(1, -1, 0), Vec3(0, 1, 0)) == Vec3(1, 1, 0)
    # 反射保持长度
    r = Vec3.reflect(Vec3(2, -3, 5), Vec3(0, 1, 0))
    assert r.length() == pytest.approx(Vec3(2, -3, 5).length(), abs=1e-12)


def test_refract():
    # 竖直入射应近似原方向
    r = Vec3.refract(Vec3(0, -1, 0), Vec3(0, 1, 0), 1.0 / 1.5)
    assert (r - Vec3(0, -1, 0)).length() < 1e-12
    assert r.length() == pytest.approx(1.0, abs=1e-12)

    # 任意方向折射后仍为单位向量
    for _ in range(50):
        n = Vec3.random_unit_vector()
        d = Vec3.random_on_hemisphere(-n)  # 入射指向表面
        refr = Vec3.refract(d, n, 1.0 / 1.5)
        assert refr.length() == pytest.approx(1.0, abs=1e-12)


# ---------------------------------------------------------------------------
# __repr__ 可还原
# ---------------------------------------------------------------------------
def test_repr_roundtrip(v: Vec3):
    assert eval(repr(v)) == v
