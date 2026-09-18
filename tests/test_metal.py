"""Metal 类的 pytest 测试（由 material/Metal.py 原 __main__ 自测块迁移而来）。

运行：
    .venv/bin/python -m pytest tests/test_metal.py -v
"""

import pytest

from Color import Color
from HitRecord import HitRecord
from Point3 import Point3
from Ray import Ray
from Vec3 import Vec3
from material.Metal import Metal


@pytest.fixture
def outer_hit() -> HitRecord:
    """命中水平面：法线 (0,1,0)，front_face=True。"""
    return HitRecord(point=Point3(0, 0, 0), normal=Vec3(0, 1, 0), t=1.0, front_face=True)


def test_albedo_and_default_fuzz():
    mat = Metal(Color(0.8, 0.8, 0.8))
    assert mat.albedo == Color(0.8, 0.8, 0.8)
    assert mat.fuzz == 0.0


def test_scatter_perfect_specular(outer_hit: HitRecord):
    # fuzz=0 退化为完美镜面：竖直入射 (0,-1,0) 反射为 (0,1,0)
    mat = Metal(Color(0.8, 0.8, 0.8), fuzz=0.0)
    result = mat.scatter(Ray(Point3(0, -1, 0), Vec3(0, -1, 0)), outer_hit)
    assert result is not None
    atten, scattered = result
    assert atten == mat.albedo
    assert scattered.direction == Vec3(0, 1, 0)


def test_scatter_fuzzy_deviates_from_specular(outer_hit: HitRecord):
    # 带 fuzz 的磨砂金属：反射方向应偏离理想镜面方向（书里不重新归一化）
    fuzzy = Metal(Color(1, 1, 1), fuzz=0.5)
    result = fuzzy.scatter(Ray(Point3(0, -1, 0), Vec3(0, -1, 0)), outer_hit)
    assert result is not None
    _, scattered = result
    assert scattered.direction != Vec3(0, 1, 0)


def test_fuzz_clamped_to_one():
    # 传入 >1 应被钳到 1
    clamped = Metal(Color(1, 1, 1), fuzz=1.5)
    assert clamped.fuzz == 1.0
