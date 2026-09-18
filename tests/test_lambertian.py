"""Lambertian 类的 pytest 测试（由 material/Lambertian.py 原 __main__ 自测块迁移而来）。

运行：
    .venv/bin/python -m pytest tests/test_lambertian.py -v
"""

import pytest

from Color import Color
from HitRecord import HitRecord
from Point3 import Point3
from Ray import Ray
from Vec3 import Vec3
from material.Lambertian import Lambertian


@pytest.fixture
def mat() -> Lambertian:
    return Lambertian(Color(0.5, 0.5, 0.5))


@pytest.fixture
def hit_record() -> HitRecord:
    """命中于原点、法线朝 +y 的命中记录。"""
    return HitRecord(
        point=Point3(0, 0, 0),
        normal=Vec3(0, 1, 0),
        t=1.0,
        front_face=True,
    )


def test_albedo(mat: Lambertian):
    assert mat.albedo == Color(0.5, 0.5, 0.5)


def test_scatter_returns_attenuation_and_ray(mat: Lambertian, hit_record: HitRecord):
    result = mat.scatter(Ray(Point3(0, 0, 0), Vec3(0, -1, 0)), hit_record)
    assert result is not None
    atten, scattered = result
    assert atten == mat.albedo


def test_scatter_origin_is_hit_point(mat: Lambertian, hit_record: HitRecord):
    _, scattered = mat.scatter(Ray(Point3(0, 0, 0), Vec3(0, -1, 0)), hit_record)
    assert scattered.origin == hit_record.point


def test_scatter_direction_in_normal_hemisphere(mat: Lambertian, hit_record: HitRecord):
    # 漫反射散射方向应落在法线所在半球（与法线点积 > 0）
    for _ in range(50):
        _, scattered = mat.scatter(Ray(Point3(0, 0, 0), Vec3(0, -1, 0)), hit_record)
        assert scattered.direction.dot(hit_record.normal) > 0
