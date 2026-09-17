from abc import ABC, abstractmethod

from Color import Color
from HitRecord import HitRecord
from Ray import Ray


class Material(ABC):
    """
    材质抽象基类

    决定一条光线击中物体表面后如何散射（或被吸收），是着色逻辑的核心。
    对应《Ray Tracing in One Weekend》中的 material 抽象类：

        class material {
          public:
            virtual ~material() = default;
            virtual bool scatter(
                const ray& r_in, const hit_record& rec,
                color& attenuation, ray& scattered
            ) const { return false; }
        };

    C++ 版本通过返回 bool 并写入 attenuation / scattered 两个「出参引用」来传达结果；
    在 Python 中我们直接返回 (attenuation, scattered) 元组，未散射时返回 None，语义等价。
    """

    @abstractmethod
    def scatter(self, r_in: Ray, rec: HitRecord) -> tuple[Color, Ray] | None:
        """
        计算入射光线 r_in 在 rec 处命中后的散射结果。

        子类必须实现本方法。

        Args:
            r_in (Ray): 入射光线。
            rec (HitRecord): 命中记录（交点、法线、t、front_face 等）。

        Returns:
            tuple[Color, Ray] | None:
                若发生散射，返回 (衰减系数 attenuation, 散射光线 scattered)；
                若光线被吸收（无散射），返回 None。
        """
        ...


if __name__ == "__main__":
    from Point3 import Point3
    from Vec3 import Vec3

    # 抽象基类本身不可实例化
    try:
        Material()
        raise AssertionError("Material 应当无法被直接实例化")
    except TypeError:
        pass

    # 一个最小可实例化的具体子类，用于验证接口形态
    class DummyMaterial(Material):
        def scatter(self, r_in: Ray, rec: HitRecord) -> tuple[Color, Ray] | None:
            atten = Color(0.5, 0.5, 0.5)
            scattered = Ray(rec.point, rec.normal)
            return atten, scattered

    rec = HitRecord(
        point=Point3(0, 0, 0),
        normal=Vec3(0, 1, 0),
        t=1.0,
        front_face=True,
    )
    m = DummyMaterial()
    result = m.scatter(Ray(Point3(0, 0, 0), Vec3(0, -1, 0)), rec)
    assert result is not None
    atten, scattered = result
    assert atten == Color(0.5, 0.5, 0.5)
    assert scattered.origin == rec.point
    print("\n所有测试通过")
