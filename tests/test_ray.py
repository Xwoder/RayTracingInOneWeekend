"""Ray 类的 pytest 测试（由 Ray.py 原 __main__ 自测块迁移而来）。

运行：
    .venv/bin/python -m pytest tests/test_ray.py -v
"""

import pytest

from Point3 import Point3
from Ray import Ray
from Vec3 import Vec3


@pytest.fixture
def ray() -> Ray:
    """原点 (0,0,0)、方向 (1,2,3) 的光线。"""
    return Ray(Point3(0, 0, 0), Vec3(1, 2, 3))


def test_constructor_and_accessors(ray: Ray):
    assert ray.origin == Point3(0, 0, 0)
    assert ray.direction == Vec3(1, 2, 3)


@pytest.mark.parametrize(
    "t, expected",
    [
        (0, Point3(0, 0, 0)),
        (1, Point3(1, 2, 3)),
        (2.5, Point3(2.5, 5.0, 7.5)),
    ],
)
def test_at(ray: Ray, t: float, expected: Point3):
    assert ray.at(t) == expected
