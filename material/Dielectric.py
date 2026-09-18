import math
from typing import override

from Color import Color
from HitRecord import HitRecord
from material.Material import Material
from Number import Number
from Ray import Ray
from Vec3 import Vec3


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

    @override
    def scatter(self,
                ray_in: Ray,
                hit_record: HitRecord) -> tuple[Color, Ray] | None:
        """
        在命中处产生一条折射（或全内反射）光线。

        Args:
            ray_in (Ray): 入射光线。
            hit_record (HitRecord): 命中记录（提供交点、法线、front_face）。

        Returns:
            tuple[Color, Ray] | None: 始终返回 (纯白衰减, 出射光线)；
                可折射时出射为折射光线，全内反射时出射为反射光线。
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

        # 若 ri * sin_theta > 1.0 则无法折射（全内反射），回退为镜面反射
        cannot_refract: bool = ri * sin_theta > 1.0

        if cannot_refract:
            direction: Vec3 = Vec3.reflect(unit_direction, hit_record.normal)
        else:
            direction = Vec3.refract(unit_direction, hit_record.normal, ri)

        scattered_ray: Ray = Ray(hit_record.point, direction)
        return attenuation, scattered_ray


if __name__ == "__main__":
    from Point3 import Point3

    mat = Dielectric(1.5)
    print(f"refraction_index: {mat.refraction_index}")
    assert mat.refraction_index == 1.5

    # 竖直入射 (0,-1,0) 打到水平面法线 (0,1,0)，玻璃(η=1.5) 内部：
    # front_face=True -> ri = 1/1.5，折射方向仍竖直向下 (0,-1,0)
    rec = HitRecord(
        point=Point3(0, 0, 0),
        normal=Vec3(0, 1, 0),
        t=1.0,
        front_face=True,
    )
    result = mat.scatter(Ray(Point3(0, 0, 0), Vec3(0, -1, 0)), rec)
    assert result is not None
    atten, scattered = result
    assert atten == Color(1.0, 1.0, 1.0)
    # 折射方向应为单位向量（竖直入射不偏折）
    assert abs(scattered.direction.length() - 1.0) < 1e-12
    assert (scattered.direction - Vec3(0, -1, 0)).length() < 1e-12
    # 散射光线应从命中点发出
    assert scattered.origin == rec.point

    # 从内部射出：front_face=False -> ri = 1.5
    rec_inner = HitRecord(
        point=Point3(0, 0, 0),
        normal=Vec3(0, -1, 0),
        t=1.0,
        front_face=False,
    )
    res2 = mat.scatter(Ray(Point3(0, 0, 0), Vec3(0, -1, 0)), rec_inner)
    assert res2 is not None
    atten2, scattered2 = res2
    assert atten2 == Color(1.0, 1.0, 1.0)
    assert abs(scattered2.direction.length() - 1.0) < 1e-12

    # 全内反射（TIR）：玻璃(η=1.5)内部以极大掠射角射向空气(η=1.0)。
    # 此时 ri = 1.5，需 sin_theta > 1/1.5 ≈ 0.667 才会无法折射。
    # 取入射方向 (0, 0.3, 0.954)（与法线 (0,-1,0) 几乎平行，sin≈0.954），
    # 则 ri*sin_theta ≈ 1.5*0.954 = 1.431 > 1.0 -> cannot_refract，走反射分支。
    # 注意法线 (0,-1,0) 指向内侧（与入射方向相反，满足 dot(dir,normal)<0）。
    tir_dir = Vec3(0, 0.3, 0.954).unit_vector()
    rec_tir = HitRecord(
        point=Point3(0, 0, 0),
        normal=Vec3(0, -1, 0),
        t=1.0,
        front_face=False,   # 从内部射出
    )
    res_tir = mat.scatter(Ray(Point3(0, 0, 0), tir_dir), rec_tir)
    assert res_tir is not None
    atten_tir, scattered_tir = res_tir
    assert atten_tir == Color(1.0, 1.0, 1.0)
    # 全内反射的分支应走 reflect，而非 refract：
    # reflect(tir_dir, normal) = tir_dir - 2*dot*tir_dir·n
    expected_reflect = Vec3.reflect(tir_dir, rec_tir.normal)
    assert (scattered_tir.direction - expected_reflect).length() < 1e-12

    print("\n所有测试通过")
