#!/usr/bin/python

import math

from Camera import Camera
from Color import Color
from HittableList import HittableList
from Point3 import Point3
from Sphere import Sphere
from Vec3 import Vec3
from material.Dielectric import Dielectric
from material.Lambertian import Lambertian
from material.Metal import Metal


def main_world_1() -> None:
    # 场景
    world: HittableList = HittableList()
    # 大地平面：球心 (0,-100.5,-1)，半径 100（模拟地面）
    material_ground = Lambertian(Color(0.8, 0.8, 0.0))
    # 中间小球：朗伯材质
    material_center = Lambertian(Color(0.1, 0.2, 0.5))
    # 左侧小球：电介质（玻璃）材质，折射率 1.50
    material_left = Dielectric(1.50)
    # 左侧小球内部的「气泡」：相对折射率 1.00 / 1.50 的电介质空腔
    material_bubble = Dielectric(1.00 / 1.50)
    # 右侧小球：金属材质（fuzz 0.0，完美镜面）
    material_right = Metal(Color(0.8, 0.6, 0.2), 0.0)

    world.add(Sphere(Point3(0.0, -100.5, -1.0), 100.0, material_ground))
    world.add(Sphere(Point3(0.0, 0.0, -1.2), 0.5, material_center))
    world.add(Sphere(Point3(-1.0, 0.0, -1.0), 0.5, material_left))
    world.add(Sphere(Point3(-1.0, 0.0, -1.0), 0.4, material_bubble))
    world.add(Sphere(Point3(1.0, 0.0, -1.0), 0.5, material_right))

    # Image
    aspect_ratio = 16 / 9
    image_width = 800

    # Camera（内部完成视口、像素网格计算与渲染）
    camera = Camera(aspect_ratio=aspect_ratio,
                    image_width=image_width)
    camera.render(world)


def main_world_2() -> None:
    # 场景：两个 Lambertian 小球（左蓝、右红）
    world: HittableList = HittableList()

    R = math.cos(math.pi / 4)

    material_left = Lambertian(Color(0, 0, 1))
    material_right = Lambertian(Color(1, 0, 0))

    world.add(Sphere(Point3(-R, 0, -1), R, material_left))
    world.add(Sphere(Point3(R, 0, -1), R, material_right))

    # Camera
    camera = Camera(aspect_ratio=16.0 / 9.0,
                    image_width=800,
                    samples_per_pixel=100,
                    max_depth=50,
                    vfov=90)
    camera.render(world)


def main_world_3() -> None:
    # 场景：与 main_world_1 相同布局，但使用带磨砂的金属、并通过相机姿态观察
    #   - 地面：黄色朗伯
    #   - 中间：蓝色朗伯小球
    #   - 左侧：折射率 1.50 的玻璃球，内含相对折射率 1/1.50 的气泡
    #   - 右侧：fuzz=1.0 的橙色磨砂金属球
    world: HittableList = HittableList()

    material_ground = Lambertian(Color(0.8, 0.8, 0.0))
    material_center = Lambertian(Color(0.1, 0.2, 0.5))
    material_left = Dielectric(1.50)
    material_bubble = Dielectric(1.00 / 1.50)
    material_right = Metal(Color(0.8, 0.6, 0.2), 1.0)

    world.add(Sphere(Point3(0.0, -100.5, -1.0), 100.0, material_ground))
    world.add(Sphere(Point3(0.0, 0.0, -1.2), 0.5, material_center))
    world.add(Sphere(Point3(-1.0, 0.0, -1.0), 0.5, material_left))
    world.add(Sphere(Point3(-1.0, 0.0, -1.0), 0.4, material_bubble))
    world.add(Sphere(Point3(1.0, 0.0, -1.0), 0.5, material_right))

    # Camera
    camera = Camera(aspect_ratio=16.0 / 9.0,
                    image_width=400,
                    samples_per_pixel=100,
                    max_depth=50,
                    vfov=90,
                    lookfrom=Point3(-2, 2, 1),
                    lookat=Point3(0, 0, -1),
                    vup=Vec3(0, 1, 0))
    camera.render(world)


if __name__ == "__main__":
    main_world_3()
