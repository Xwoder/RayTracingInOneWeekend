#!/usr/bin/python

from Camera import Camera
from Color import Color
from HittableList import HittableList
from Lambertian import Lambertian
from Point3 import Point3
from Sphere import Sphere


def main() -> None:
    # 场景
    world: HittableList = HittableList()
    # 小球体：球心 (0,0,-1)，半径 0.5
    world.add(Sphere(Point3(0, 0, -1), 0.5, Lambertian(Color(0.7, 0.3, 0.3))))
    # 大地平面：球心 (0,-100.5,-1)，半径 100（模拟地面）
    world.add(Sphere(Point3(0, -100.5, -1), 100, Lambertian(Color(0.3, 0.7, 0.3))))

    # Image
    aspect_ratio = 16 / 9
    image_width = 800

    # Camera（内部完成视口、像素网格计算与渲染）
    camera = Camera(aspect_ratio=aspect_ratio,
                    image_width=image_width)
    camera.render(world)


if __name__ == "__main__":
    main()
