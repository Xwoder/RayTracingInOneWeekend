#!/usr/bin/python

from Camera import Camera
from Color import Color
from HittableList import HittableList
from material.Dielectric import Dielectric
from material.Lambertian import Lambertian
from material.Metal import Metal
from Point3 import Point3
from Sphere import Sphere


def main() -> None:
    # 场景
    world: HittableList = HittableList()
    # 大地平面：球心 (0,-100.5,-1)，半径 100（模拟地面）
    material_ground = Lambertian(Color(0.8, 0.8, 0.0))
    # 中间小球：朗伯材质
    material_center = Lambertian(Color(0.1, 0.2, 0.5))
    # 左侧小球：电介质（玻璃）材质，折射率 1.50
    material_left = Dielectric(1.50)
    # 右侧小球：金属材质（磨砂 1.0，被钳制为最大毛糙）
    material_right = Metal(Color(0.8, 0.6, 0.2), 1.0)

    world.add(Sphere(Point3(0.0, -100.5, -1.0), 100.0, material_ground))
    world.add(Sphere(Point3(0.0, 0.0, -1.2), 0.5, material_center))
    world.add(Sphere(Point3(-1.0, 0.0, -1.0), 0.5, material_left))
    world.add(Sphere(Point3(1.0, 0.0, -1.0), 0.5, material_right))

    # Image
    aspect_ratio = 16 / 9
    image_width = 800

    # Camera（内部完成视口、像素网格计算与渲染）
    camera = Camera(aspect_ratio=aspect_ratio,
                    image_width=image_width)
    camera.render(world)


if __name__ == "__main__":
    main()
