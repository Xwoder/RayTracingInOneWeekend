#!/usr/bin/python

import math
import sys

from Camera import Camera
from Color import Color, write_color
from HitRecord import HitRecord
from HittableList import HittableList
from Interval import Interval
from Point3 import Point3
from Ray import Ray
from Sphere import Sphere
from Vec3 import Vec3

# 场景
world: HittableList = HittableList()
# 小球体：球心 (0,0,-1)，半径 0.5
world.add(Sphere(Point3(0, 0, -1), 0.5))
# 大地平面：球心 (0,-100.5,-1)，半径 100（模拟地面）
world.add(Sphere(Point3(0, -100.5, -1), 100))


def ray_color(ray: Ray, world: HittableList) -> Color:
    """
    计算光线在场景中的着色颜色（对应《Ray Tracing in One Weekend》的 ray_color）。

    若光线与场景中的任意物体相交，则以交点处的单位法线映射为 RGB 颜色返回；
    否则返回按光线方向 y 分量插值出的天空渐变背景色。

    Args:
        ray (Ray): 待着色的光线，其原点为相机位置，方向指向当前像素。
        world (HittableList): 待检测的场景（可命中物体列表）。

    Returns:
        Color: 该光线对应的颜色。命中物体时为法线映射色
            0.5 * (N + 1)；未命中时为天空渐变背景色。
    """
    # world.hit 命中时返回 HitRecord，未命中返回 None（对应 C++ 的 world.hit(r, interval(0, inf), hit_record)）
    hit_record: HitRecord | None = world.hit(ray, Interval(0.0, math.inf))
    if hit_record is not None:
        # 命中：以交点处单位法线映射到 RGB 着色（0.5 * (N + 1)）
        return 0.5 * (hit_record.normal + Color(1.0, 1.0, 1.0))
    else:
        # 未命中：返回天空渐变背景
        unit_direction = ray.direction.unit_vector()
        a = 0.5 * (unit_direction.y + 1.0)
        return (1.0 - a) * Color(1.0, 1.0, 1.0) + a * Color(0.5, 0.7, 1.0)


def main() -> None:
    # Image
    aspect_ratio = 16 / 9
    image_width = 800
    image_height = int(image_width / aspect_ratio)
    image_height = 1 if image_height < 1 else image_height

    # Camera
    camera = Camera()
    focal_length = 1.0
    focal_direction = Vec3(0, 0, focal_length)

    # Viewport widths less than one are ok since they are real valued.
    viewport_height = 2.0
    viewport_width = viewport_height * (image_width / image_height)

    # Calculate the vectors across the horizontal and down the vertical viewport edges.
    viewport_u: Vec3 = Vec3(viewport_width, 0, 0)
    viewport_v: Vec3 = Vec3(0, -viewport_height, 0)

    # Calculate the horizontal and vertical delta vectors from pixel to pixel.
    pixel_delta_u: Vec3 = viewport_u / image_width
    pixel_delta_v: Vec3 = viewport_v / image_height

    # Calculate the location of the upper left pixel.
    viewport_center = camera.position - focal_direction
    viewport_upper_left = viewport_center - viewport_u / 2 - viewport_v / 2
    pixel00_loc = viewport_upper_left + (pixel_delta_u + pixel_delta_v) / 2

    out_std = sys.stdout
    out_err = sys.stderr

    # Render
    out_std.write(f"P3\n{image_width} {image_height}\n255\n")

    for row in range(image_height):
        out_err.write(f"Rendering row {row}\n")
        for col in range(image_width):
            pixel_center = pixel00_loc + (col * pixel_delta_u) + (row * pixel_delta_v)
            ray_direction = pixel_center - camera.position
            ray: Ray = Ray(camera.position, ray_direction)
            pixel_color = ray_color(ray, world)
            write_color(out_std, pixel_color)
    out_std.write("Done")


if __name__ == "__main__":
    main()
