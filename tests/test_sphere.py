"""Sphere 类的 pytest 测试（由 Sphere.py 原 __main__ 自测块迁移而来）。

运行：
    .venv/bin/python -m pytest tests/test_sphere.py -v
"""

import pytest

from Color import Color
from HitRecord import HitRecord
from Interval import Interval
from Point3 import Point3
from Ray import Ray
from Sphere import Sphere
from Vec3 import Vec3
from material.Material import Material


class DummyMaterial(Material):
    """仅用于测试的最小可实例化材质。"""

    def scatter(self, ray_in, hit_record):
        return Color(0.5, 0.5, 0.5), Ray(hit_record.point, hit_record.normal)


@pytest.fixture
def sphere() -> Sphere:
    """球心 (0,0,0)、半径 1.5 的球，带 DummyMaterial。"""
    return Sphere(Point3(0, 0, 0), 1.5, DummyMaterial())


@pytest.fixture
def hitting_ray() -> Ray:
    """沿 +z 从 (0,0,-5) 射向球心在原点的球，两根 t 为 3.5 与 6.5。"""
    return Ray(Point3(0, 0, -5), Vec3(0, 0, 1))


# ---------------------------------------------------------------------------
# 构造 / 属性 / repr
# ---------------------------------------------------------------------------
def test_constructor_and_accessors(sphere: Sphere):
    assert sphere.center == Point3(0, 0, 0)
    assert sphere.radius == 1.5


def test_repr_contains_material(sphere: Sphere):
    assert "material=" in repr(sphere)


# ---------------------------------------------------------------------------
# hit：命中几何 / 法线 / 材质
# ---------------------------------------------------------------------------
def test_hit_records_intersection(sphere: Sphere, hitting_ray: Ray):
    rec = sphere.hit(hitting_ray)
    assert rec is not None
    assert rec.t == pytest.approx(3.5, abs=1e-9)
    assert rec.point == Point3(0, 0, -1.5)
    # 光线从球外射入 -> 正面；法线指向光线来的一侧（-z）
    assert rec.front_face is True
    assert rec.normal == Vec3(0, 0, -1)
    assert hitting_ray.direction.dot(rec.normal) < 0
    # 命中记录携带本球材质
    assert rec.material is sphere._material


def test_miss_returns_none(sphere: Sphere):
    r_miss = Ray(Point3(5, 0, -5), Vec3(0, 0, 1))
    assert sphere.hit(r_miss) is None


# ---------------------------------------------------------------------------
# hit：t 区间限制（开区间，取区间内最近根）
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "interval, expected_t",
    [
        (Interval(0.0, 100.0), 3.5),   # 近根 3.5 落在区间内
        (Interval(0.0, 3.0), None),    # 上界过小，两根本排除
        (Interval(4.0, 100.0), 6.5),   # 近根被排除，取远根 6.5
        (Interval(7.0, 100.0), None),  # 两根本排除
    ],
)
def test_hit_t_interval(sphere: Sphere, hitting_ray: Ray, interval: Interval, expected_t):
    rec = sphere.hit(hitting_ray, interval)
    if expected_t is None:
        assert rec is None
    else:
        assert rec is not None
        assert rec.t == pytest.approx(expected_t, abs=1e-9)


# ---------------------------------------------------------------------------
# hit：光线从球内射出 -> 命中背面，法线翻向光线来的一侧
# ---------------------------------------------------------------------------
def test_hit_from_inside(sphere: Sphere):
    r_inside = Ray(Point3(0, 0, 0), Vec3(0, 0, 1))
    rec = sphere.hit(r_inside)
    assert rec is not None
    assert rec.front_face is False
    assert rec.normal == Vec3(0, 0, -1)
    assert r_inside.direction.dot(rec.normal) < 0
