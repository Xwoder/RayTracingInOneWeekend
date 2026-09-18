import math
from typing import override

from Color import Color
from HitRecord import HitRecord
from Number import Number
from Random import random_number
from Ray import Ray
from Vec3 import Vec3
from material.Material import Material


class Dielectric(Material):
    """
    电介质（透明折射）材质，如玻璃、水、钻石

    对应《Ray Tracing in One Weekend》中的 dielectric 类。命中后光线按相对折射率
    发生折射（而非反射/漫反射），衰减系数恒为纯白 color(1,1,1)，即光线本身不
    被吸收着色，仅改变传播方向。

    折射率 refraction_index 表示真空/空气中的折射率，或「本材质折射率 / 包围介质
    折射率」的比值。从外表面入射时使用 1.0/refraction_index，从内表面射出时
    （front_face 为 False）使用 refraction_index（对应 C++ 中
    rec.front_face ? (1.0/refraction_index) : refraction_index）。

    当入射角过大导致 sin(theta') > 1（即 ri * sin_theta > 1.0，全内反射 TIR）
    时，无法折射，此时回退为镜面反射（对应 C++ 中 cannot_refract 分支）。

    即便可以折射，也按 Schlick 近似计算出的反射率 reflectance 概率性地选择
    反射而非折射，从而正确呈现玻璃在掠射角下更亮、以及菲涅尔效应带来的
    边缘反光（对应 C++ 中 `cannot_refract || reflectance(...) > random_double()`）。
    """

    _refraction_index: Number

    def __init__(self,
                 refraction_index: Number):
        """
        构造一个电介质材质。

        Args:
            refraction_index (Number): 折射率（真空/空气下的值）。
        """
        self._refraction_index = refraction_index

    @property
    def refraction_index(self) -> Number:
        """返回折射率。"""
        return self._refraction_index

    @staticmethod
    def reflectance(cosine: Number, refraction_index: Number) -> Number:
        """
        用 Schlick 近似估算给定入射角余弦下的反射率（菲涅尔反射比例）。
        对应 C++ 的静态函数 reflectance(cosine, refraction_index)：

            auto r0 = (1 - refraction_index) / (1 + refraction_index);
            r0 = r0 * r0;
            return r0 + (1 - r0) * pow(1 - cosine, 5);

        注意：此处传入的是相对折射率 ri（与 C++ 一致），而非成员 refraction_index。

        Args:
            cosine (Number): 入射角余弦（对应 cos_theta）。
            refraction_index (Number): 相对折射率（etai_over_etat）。

        Returns:
            Number: 反射率，取值范围 [0,1]。
        """
        r0: Number = (1 - refraction_index) / (1 + refraction_index)
        r0 = r0 * r0
        return r0 + (1 - r0) * (1 - cosine) ** 5

    @override
    def scatter(self,
                ray_in: Ray,
                hit_record: HitRecord) -> tuple[Color, Ray] | None:
        """
        在命中处产生一条折射、全内反射或菲涅尔反射光线。

        Args:
            ray_in (Ray): 入射光线。
            hit_record (HitRecord): 命中记录（提供交点、法线、front_face）。

        Returns:
            tuple[Color, Ray] | None: 始终返回 (纯白衰减, 出射光线)：
                - 无法折射（全内反射）时走反射分支；
                - 否则按 Schlick 近似反射率概率性地选择反射或折射。
        """
        # 电介质本身不吸收颜色，衰减即为全白
        attenuation: Color = Color(1.0, 1.0, 1.0)

        # 相对折射率：由外入内用 1/eta，由内出外用 eta
        ri: Number = (1.0 / self._refraction_index) if hit_record.front_face else self._refraction_index

        # 入射方向归一化为单位向量
        unit_direction: Vec3 = ray_in.direction.unit_vector()

        # 入射角余弦（钳制到 1.0 以避免数值误差越界），对应 C++ 的 cos_theta
        cos_theta: Number = min(-unit_direction.dot(hit_record.normal), 1.0)
        # 由三角恒等式 sin²θ = 1 - cos²θ 得到 sin_theta
        sin_theta: Number = math.sqrt(1.0 - cos_theta * cos_theta)

        # 若 ri * sin_theta > 1.0 则无法折射（全内反射）
        cannot_refract: bool = ri * sin_theta > 1.0

        # 全内反射，或按 Schlick 近似反射率概率性选择反射；否则折射
        if cannot_refract or self.reflectance(cos_theta, ri) > random_number():
            direction: Vec3 = Vec3.reflect(unit_direction, hit_record.normal)
        else:
            direction = Vec3.refract(unit_direction, hit_record.normal, ri)

        scattered_ray: Ray = Ray(hit_record.point, direction)
        return attenuation, scattered_ray


