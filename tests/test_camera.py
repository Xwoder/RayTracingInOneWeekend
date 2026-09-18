"""Camera 类的 pytest 测试（由 Camera.py 原 __main__ 自测块迁移而来）。

运行：
    .venv/bin/python -m pytest tests/test_camera.py -v
"""

import io

import pytest

from Camera import Camera
from Color import Color
from HittableList import HittableList
from Point3 import Point3
from Ray import Ray
from Vec3 import Vec3
from material.Lambertian import Lambertian
from Sphere import Sphere


@pytest.fixture
def camera_16_9() -> Camera:
    """宽高比 16/9、宽 400 的相机（已 initialize）。"""
    cam = Camera(aspect_ratio=16 / 9, image_width=400)
    cam.initialize()
    return cam


# ---------------------------------------------------------------------------
# initialize：尺寸 / 视口 / 像素网格
# ---------------------------------------------------------------------------
def test_initialize_image_height(camera_16_9: Camera):
    assert camera_16_9.image_height == 225


def test_center_at_origin(camera_16_9: Camera):
    assert camera_16_9.center == Point3(0, 0, 0)


def test_viewport_width_matches_aspect_ratio(camera_16_9: Camera):
    expected_viewport_width = 2.0 * (400 / 225)
    derived = camera_16_9.pixel_delta_u.x * camera_16_9.image_width
    assert derived == pytest.approx(expected_viewport_width, abs=1e-9)


def test_pixel00_loc_at_focal_distance(camera_16_9: Camera):
    # 像素(0,0)位于视口左上角内侧半格，z 应为 -1（焦距 1.0）
    assert camera_16_9.pixel00_loc.z == pytest.approx(-1.0, abs=1e-9)


def test_sample_square_range():
    cam = Camera()
    for _ in range(100):
        s = cam.sample_square()
        assert -0.5 <= s.x < 0.5
        assert -0.5 <= s.y < 0.5
        assert s.z == 0


# ---------------------------------------------------------------------------
# ray_color：深度耗尽 / 天空渐变背景
# ---------------------------------------------------------------------------
def test_ray_color_depth_zero_is_black():
    cam = Camera()
    world = HittableList()
    r = Ray(Point3(0, 0, 0), Vec3(0, 0, -1))
    assert cam.ray_color(r, 0, world) == Color(0, 0, 0)


def test_ray_color_background_gradient():
    cam = Camera()
    world = HittableList()  # 空场景 -> 必走背景分支
    # 朝上：a=1 -> 蓝白色 (0.5, 0.7, 1.0)
    up = cam.ray_color(Ray(Point3(0, 0, 0), Vec3(0, 1, 0)), 1, world)
    assert up == Color(0.5, 0.7, 1.0)
    # 朝下：a=0 -> 纯白 (1, 1, 1)
    down = cam.ray_color(Ray(Point3(0, 0, 0), Vec3(0, -1, 0)), 1, world)
    assert down == Color(1.0, 1.0, 1.0)


# ---------------------------------------------------------------------------
# render：PPM 输出格式
# ---------------------------------------------------------------------------
def test_render_writes_ppm_header_and_pixels():
    tiny = Camera(aspect_ratio=1.0, image_width=3)
    world = HittableList(
        Sphere(Point3(0, 0, -1), 0.5, Lambertian(Color(0.5, 0.5, 0.5)))
    )
    buf = io.StringIO()
    tiny.render(world, out=buf)

    lines = buf.getvalue().splitlines()
    assert lines[0] == "P3"
    assert lines[1] == "3 3"
    assert lines[2] == "255"
    # 3x3 图像应有 9 行 RGB
    assert len(lines) == 3 + 9
