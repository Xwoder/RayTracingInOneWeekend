"""Dielectric 类的 pytest 测试（由 material/Dielectric.py 原 __main__ 自测块迁移而来）。

运行：
    .venv/bin/python -m pytest tests/test_dielectric.py -v

注意：scatter() 中按 Schlick 近似概率性选择反射/折射，属随机分支；
迁移时对该类用例只断言「两分支都成立的不变量」（白衰减、出射单位向量、
从命中点发出），避免 flaky。reflectance() 与全内反射分支是确定性的，精确断言。
"""

import pytest

from Color import Color
from HitRecord import HitRecord
from Point3 import Point3
from Ray import Ray
from Vec3 import Vec3
from material.Dielectric import Dielectric


@pytest.fixture
def mat() -> Dielectric:
    return Dielectric(1.5)


@pytest.fixture
def outer_hit() -> HitRecord:
    """从外射入水平面：法线 (0,1,0)，front_face=True。"""
    return HitRecord(point=Point3(0, 0, 0), normal=Vec3(0, 1, 0), t=1.0, front_face=True)


@pytest.fixture
def inner_hit() -> HitRecord:
    """从内射出水平面：法线 (0,-1,0)，front_face=False。"""
    return HitRecord(point=Point3(0, 0, 0), normal=Vec3(0, -1, 0), t=1.0, front_face=False)


def test_refraction_index(mat: Dielectric):
    assert mat.refraction_index == 1.5


# ---------------------------------------------------------------------------
# scatter：非 TIR 分支（概率性）——断言两分支都成立的不变量
# ---------------------------------------------------------------------------
def test_scatter_outer_incidence_invariants(mat: Dielectric, outer_hit: HitRecord):
    atten, scattered = mat.scatter(Ray(Point3(0, 0, 0), Vec3(0, -1, 0)), outer_hit)
    assert atten == Color(1.0, 1.0, 1.0)           # 电介质不吸收颜色
    assert scattered.direction.length() == pytest.approx(1.0, abs=1e-12)
    assert scattered.origin == outer_hit.point


def test_scatter_inner_exit_invariants(mat: Dielectric, inner_hit: HitRecord):
    atten, scattered = mat.scatter(Ray(Point3(0, 0, 0), Vec3(0, -1, 0)), inner_hit)
    assert atten == Color(1.0, 1.0, 1.0)
    assert scattered.direction.length() == pytest.approx(1.0, abs=1e-12)


# ---------------------------------------------------------------------------
# scatter：全内反射（TIR）—— 确定性走 reflect 分支
# ---------------------------------------------------------------------------
def test_scatter_total_internal_reflection(mat: Dielectric):
    # 玻璃(η=1.5)内部以极大掠射角射向空气：ri=1.5, sin_theta>1/1.5 -> 无法折射
    tir_dir = Vec3(0, 0.3, 0.954).unit_vector()
    rec_tir = HitRecord(point=Point3(0, 0, 0), normal=Vec3(0, -1, 0), t=1.0, front_face=False)
    atten, scattered = mat.scatter(Ray(Point3(0, 0, 0), tir_dir), rec_tir)
    assert atten == Color(1.0, 1.0, 1.0)
    # 全内反射必走 reflect 而非 refract
    expected_reflect = Vec3.reflect(tir_dir, rec_tir.normal)
    assert (scattered.direction - expected_reflect).length() < 1e-12


# ---------------------------------------------------------------------------
# reflectance：Schlick 近似纯函数（确定性）
# ---------------------------------------------------------------------------
def test_reflectance_vertical_incidence():
    # ri=1.5 -> r0 = ((1-1.5)/(1+1.5))² = 0.04；cosine=1 时 (1-cos)^5=0
    assert abs(Dielectric.reflectance(1.0, 1.5) - 0.04) < 1e-12


def test_reflectance_grazing():
    # cosine=0（掠射）-> r0 + (1-r0) = 1.0（完全反射）
    assert abs(Dielectric.reflectance(0.0, 1.5) - 1.0) < 1e-12


@pytest.mark.parametrize("cosine", [0.9, 0.7, 0.5, 0.3, 0.1])
def test_reflectance_in_range_and_monotonic(cosine: float):
    r = Dielectric.reflectance(cosine, 1.5)
    assert 0.0 <= r <= 1.0
    # 越接近掠射（cosine 越小）反射率越高（菲涅尔效应）
    assert r >= Dielectric.reflectance(1.0, 1.5)
