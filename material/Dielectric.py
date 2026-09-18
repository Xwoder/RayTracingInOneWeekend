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

    说明：本实现严格对应你给出的 C++ 代码，尚未加入全内反射（TIR）的反射回退
    判断，因此高角度入射（且折射后方向可能指向内侧）时仍直接按折射方向出射。
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
        在命中处产生一条折射光线。

        Args:
            ray_in (Ray): 入射光线。
            hit_record (HitRecord): 命中记录（提供交点、法线、front_face）。

        Returns:
            tuple[Color, Ray] | None: 始终返回 (纯白衰减, 折射光线)。
        """
        # 电介质本身不吸收颜色，衰减即为全白
        attenuation: Color = Color(1.0, 1.0, 1.0)

        # 相对折射率：由外入内用 1/eta，由内出外用 eta
        ri: Number = (1.0 / self._refraction_index) if hit_record.front_face else self._refraction_index

        # 入射方向归一化为单位向量
        unit_direction: Vec3 = ray_in.direction.unit_vector()

        # 按 Snell 定律计算折射方向
        refracted: Vec3 = Vec3.refract(unit_direction, hit_record.normal, ri)

        scattered_ray: Ray = Ray(hit_record.point, refracted)
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

    print("\n所有测试通过")
