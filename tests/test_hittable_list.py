"""HittableList 类的 pytest 测试（由 HittableList.py 原 __main__ 自测块迁移而来）。

运行：
    .venv/bin/python -m pytest tests/test_hittable_list.py -v
"""

import math

import pytest

from Color import Color
from HittableList import HittableList
from Interval import Interval
from Point3 import Point3
from Ray import Ray
from Sphere import Sphere
from Vec3 import Vec3
from material.Lambertian import Lambertian


@pytest.fixture
def mat() -> Lambertian:
    return Lambertian(Color(0.5, 0.5, 0.5))


@pytest.fixture
def near_far_world(mat) -> HittableList:
    """包含两个共线球的场景：近球 z=-1、远球 z=-3，半径均 0.5。"""
    world = HittableList()
    world.add(Sphere(Point3(0, 0, -1), 0.5, mat))
    world.add(Sphere(Point3(0, 0, -3), 0.5, mat))
    return world


@pytest.fixture
def down_ray() -> Ray:
    """从原点沿 -z 射出的光线。"""
    return Ray(Point3(0, 0, 0), Vec3(0, 0, -1))


# ---------------------------------------------------------------------------
# 构造 / 增删 / __len__
# ---------------------------------------------------------------------------
def test_empty_world_has_zero_objects():
    assert len(HittableList()) == 0


def test_add_then_len(near_far_world: HittableList):
    assert len(near_far_world) == 2


def test_constructor_adds_initial_object(mat):
    assert len(HittableList(Sphere(Point3(0, 0, -1), 0.5, mat))) == 1


def test_clear_empties_world(near_far_world: HittableList):
    near_far_world.clear()
    assert len(near_far_world) == 0


# ---------------------------------------------------------------------------
# hit：取最近命中、区间限制、错过、清空
# ---------------------------------------------------------------------------
def test_hit_returns_nearest(near_far_world: HittableList, down_ray: Ray):
    rec = near_far_world.hit(down_ray)
    assert rec is not None
    assert rec.t == pytest.approx(0.5, abs=1e-9)
    assert rec.point == Point3(0, 0, -0.5)
    assert rec.front_face is True  # 从球外射入，命中正面


def test_hit_respects_interval_lower_bound(near_far_world: HittableList, down_ray: Ray):
    # 下界 [2.0, +∞)：近球（t≈0.5）被排除，应命中远球（t≈2.5）
    rec_far = near_far_world.hit(down_ray, Interval(2.0, math.inf))
    assert rec_far is not None
    assert rec_far.t == pytest.approx(2.5, abs=1e-9)


def test_hit_misses_when_off_target(near_far_world: HittableList):
    r_miss = Ray(Point3(5, 0, 0), Vec3(0, 0, -1))
    assert near_far_world.hit(r_miss) is None


def test_hit_none_after_clear(near_far_world: HittableList, down_ray: Ray):
    near_far_world.clear()
    assert near_far_world.hit(down_ray) is None
