from typing import override

from Color import Color
from HitRecord import HitRecord
from Material import Material
from Ray import Ray
from Vec3 import Vec3


class Metal(Material):
    """
    金属（镜面反射）材质

    对应《Ray Tracing in One Weekend》中的 metal 类。命中后沿交点法线
    做完全镜面反射（不扩散、不随机），衰减系数即表面反照率 albedo。
    反射方向由 Vec3.reflect 计算，法线必须已为单位向量（与 C++ 实现一致）。
    """

    _albedo: Color

    def __init__(self,
                 albedo: Color):
        """
        构造一个金属材质。

        Args:
            albedo (Color): 表面反照率（对反射光的比例衰减系数）。
        """
        self._albedo = albedo

    @property
    def albedo(self) -> Color:
        """返回表面反照率。"""
        return self._albedo

    @override
    def scatter(self,
                ray_in: Ray,
                hit_record: HitRecord) -> tuple[Color, Ray] | None:
        """
        在命中处产生一条镜面反射光线。

        对应 C++ metal::scatter 的语义：
            vec3 reflected = reflect(r_in.direction(), rec.normal);
            scattered = ray(rec.p, reflected);
            attenuation = albedo;
            return true;

        Args:
            ray_in (Ray): 入射光线。
            hit_record (HitRecord): 命中记录（提供交点与法线）。

        Returns:
            tuple[Color, Ray] | None: 始终返回 (反照率, 反射光线)。
        """
        reflected: Vec3 = Vec3.reflect(ray_in.direction, hit_record.normal)
        scattered_ray: Ray = Ray(hit_record.point, reflected)
        attenuation = self._albedo
        return attenuation, scattered_ray


if __name__ == "__main__":
    from Point3 import Point3

    mat = Metal(Color(0.8, 0.8, 0.8))
    print(f"albedo: {mat.albedo}")
    assert mat.albedo == Color(0.8, 0.8, 0.8)

    # 竖直入射 (0,-1,0) 打到水平面法线 (0,1,0) 应反射为 (0,1,0)
    rec = HitRecord(
        point=Point3(0, 0, 0),
        normal=Vec3(0, 1, 0),
        t=1.0,
        front_face=True,
    )
    result = mat.scatter(Ray(Point3(0, 1, 0), Vec3(0, -1, 0)), rec)
    assert result is not None
    atten, scattered = result
    assert atten == mat.albedo
    # 反射光线从命中点发出，方向向上
    assert scattered.origin == rec.point
    assert scattered.direction == Vec3(0, 1, 0)

    print("\n所有测试通过")
