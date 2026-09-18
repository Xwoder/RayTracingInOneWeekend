from typing import override

from Color import Color
from HitRecord import HitRecord
from Number import Number
from Ray import Ray
from Vec3 import Vec3
from material.Material import Material


class Metal(Material):
    """
    金属（镜面反射）材质

    对应《Ray Tracing in One Weekend》中的 metal 类。命中后沿入射方向关于
    表面法线做镜面反射（对应 C++ 的 reflect），并始终叠加一份随机扰动以模拟
    磨砂/模糊反射（fuzz）。衰减系数即表面反照率 albedo。

    与书中实现一致：fuzz 在构造时被钳制到 [0,1]（fuzz < 1 时取原值，否则取 1）；
    fuzz 为 0 时退化为完美镜面。若扰动后的反射方向指向表面内侧
    （dot(scattered.direction, normal) <= 0），则认为光线被吸收，scatter 返回
    None（对应 C++ 中返回 false，相机端将得到黑色）。
    """

    _albedo: Color
    _fuzz: Number

    def __init__(self,
                 albedo: Color,
                 fuzz: Number = 0.0):
        """
        构造一个金属材质。

        Args:
            albedo (Color): 表面反照率（反射光的比例衰减系数）。
            fuzz (Number): 磨砂程度，构造时钳制到 [0,1]；0 为完美镜面，越大越模糊。
        """
        self._albedo = albedo
        # 钳制 fuzz 到 [0,1]（对应 C++ 的 fuzz < 1 ? fuzz : 1）
        self._fuzz = fuzz if fuzz < 1 else 1

    @property
    def albedo(self) -> Color:
        """返回表面反照率。"""
        return self._albedo

    @property
    def fuzz(self) -> Number:
        """返回磨砂程度（已被钳制到 [0,1]）。"""
        return self._fuzz

    @override
    def scatter(self,
                ray_in: Ray,
                hit_record: HitRecord) -> tuple[Color, Ray] | None:
        """
        在命中处产生一条镜面反射光线。

        Args:
            ray_in (Ray): 入射光线。
            hit_record (HitRecord): 命中记录（提供交点与法线）。

        Returns:
            tuple[Color, Ray] | None:
                若扰动后的反射方向朝外侧（dot(dir, normal) > 0），返回
                (反照率, 反射光线)；否则返回 None（光线被吸收）。
        """
        # 关于法线的理想镜面反射方向，并归一化为单位向量
        reflected: Vec3 = Vec3.reflect(ray_in.direction, hit_record.normal).unit_vector()

        # 磨砂：始终叠加 fuzz * 随机单位向量扰动（fuzz 为 0 时退化为纯镜面）
        reflected = reflected + self._fuzz * Vec3.random_unit_vector()

        scattered_ray: Ray = Ray(hit_record.point, reflected)
        # 若散射方向指向表面内侧，说明被吸收（对应 C++ 返回 false -> 黑色）
        if scattered_ray.direction.dot(hit_record.normal) <= 0:
            return None
        return self._albedo, scattered_ray
