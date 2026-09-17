from Color import Color
from HitRecord import HitRecord
from Material import Material
from Ray import Ray
from Vec3 import Vec3


class Lambertian(Material):
    """
    朗伯（理想漫反射）材质

    对应《Ray Tracing in One Weekend》中的 lambertian 类。命中后沿交点法线
    所在半球内的随机方向散射（余弦加权），衰减系数即表面反照率 albedo。

    注意：本类仅提供材质数据结构与 scatter 接口雏形，当前相机
    （Camera.ray_color）尚未使用 rec.material，因此尚未参与实际着色。
    """

    _albedo: Color

    def __init__(self,
                 albedo: Color):
        """
        构造一个朗伯材质。

        Args:
            albedo (Color): 表面反照率（对入射光的比例衰减系数）。
        """
        self._albedo = albedo

    @property
    def albedo(self) -> Color:
        """返回表面反照率。"""
        return self._albedo

    def scatter(self,
                r_in: Ray,
                rec: HitRecord) -> tuple[Color, Ray] | None:
        """
        在命中处产生一条漫反射散射光线。

        Args:
            r_in (Ray): 入射光线（此处未使用，保留以符合 Material 接口）。
            rec (HitRecord): 命中记录（提供交点与法线）。

        Returns:
            tuple[Color, Ray] | None: 始终返回 (反照率, 散射光线)。
        """
        scatter_direction: Vec3 = rec.normal + Vec3.random_unit_vector()
        scattered_ray: Ray = Ray(rec.point, scatter_direction)
        return self._albedo, scattered_ray


if __name__ == "__main__":
    from Point3 import Point3

    mat = Lambertian(Color(0.5, 0.5, 0.5))
    print(f"albedo: {mat.albedo}")
    assert mat.albedo == Color(0.5, 0.5, 0.5)

    rec = HitRecord(
        point=Point3(0, 0, 0),
        normal=Vec3(0, 1, 0),
        t=1.0,
        front_face=True,
    )
    result = mat.scatter(Ray(Point3(0, 0, 0), Vec3(0, -1, 0)), rec)
    assert result is not None
    atten, scattered = result
    assert atten == mat.albedo
    # 散射光线应从命中点发出
    assert scattered.origin == rec.point

    print("\n所有测试通过")
