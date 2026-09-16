import math
from typing import override

from HitRecord import HitRecord
from Hittable import Hittable
from Number import Number
from Point3 import Point3
from Ray import Ray
from Vec3 import Vec3


class Sphere(Hittable):
    """
    球体类

    一个球体由球心 center 与半径 radius 定义。
    实现 Hittable 接口，提供光线-球体相交检测 hit()。
    """

    _center: Point3
    _radius: Number

    def __init__(self, center: Point3, radius: Number):
        """
        构造一个球体。

        Args:
            center (Point3): 球心坐标。
            radius (Number): 球的半径（float 或 int）。
        """
        self._center = center
        self._radius = radius

    @property
    def center(self) -> Point3:
        """返回球心（对应 C++ const point3& center()）。"""
        return self._center

    @property
    def radius(self) -> Number:
        """返回半径（对应 C++ double radius()）。"""
        return self._radius

    def __repr__(self) -> str:
        """
        返回球体的官方字符串表示，形如 Sphere(center=..., radius=...)。
        其输出应满足 eval(repr(s)) 可还原出等价对象。

        Returns:
            str: 包含球心与半径的字符串表示
        """
        return f"Sphere(center={self._center!r}, radius={self._radius!r})"

    def __eq__(self, other: object) -> bool:
        """
        相等判断（s == u），当球心与半径都相等时返回 True。
        对应 C++ 的 operator==。若 other 不是 Sphere，则返回 NotImplemented
        交由 Python 处理（通常得到 False）。

        Args:
            other (object): 比较对象。

        Returns:
            bool: 球心与半径是否全部相等
        """
        if not isinstance(other, Sphere):
            return NotImplemented
        return self._center == other.center and self._radius == other.radius

    @override
    def hit(
            self,
            ray: Ray,
            ray_t_min: Number = 0.0,
            ray_t_max: Number = math.inf,
    ) -> HitRecord | None:
        """
        判断光线是否击中本球体，命中时返回记录交点信息的 HitRecord。

        对应《Ray Tracing in One Weekend》中 hittable::hit 的球体实现。
        求解球面方程 |P(t) - center|² = radius² 的展开式，引入中间变量 h 简化计算：
            oc          = center - origin
            a           = dot(dir, dir)
            h           = dot(dir, oc)
            c           = dot(oc, oc) - radius²
            discriminant = h² - a·c
        若判别式 < 0 则无实交点，返回 None；否则依次检验两根是否在 [t_min, t_max]
        区间内，取落在区间内的最近交点 t，构造包含交点坐标 p、参数 t 的
        HitRecord，并用单位外法向量 outward_normal = (p - center) / radius
        调用 set_face_normal() 写入 front_face 与 normal（法线恒朝向光线来的一侧）。

        Args:
            ray (Ray): 待检测的光线。
            ray_t_min (Number): 光线参数 t 的下界（不含），默认 0.0。
            ray_t_max (Number): 光线参数 t 的上界（不含），默认为正无穷。

        Returns:
            HitRecord | None: 命中时返回填充好的 HitRecord，未命中返回 None。
        """
        oc: Vec3 = self._center - ray.origin

        a: Number = ray.direction.length_squared()
        h: Number = ray.direction.dot(oc)
        c: Number = oc.length_squared() - self._radius ** 2
        discriminant: Number = h ** 2 - a * c
        if discriminant < 0:
            return None

        sqrt_d: Number = math.sqrt(discriminant)
        root: Number = (h - sqrt_d) / a

        if not (ray_t_min < root < ray_t_max):
            root = (h + sqrt_d) / a

            if not (ray_t_min < root < ray_t_max):
                return None

        p: Point3 = ray.at(root)
        t: Number = root
        outward_normal: Vec3 = (p - self._center) / self._radius
        rec: HitRecord = HitRecord(p, outward_normal, t)
        rec.set_face_normal(ray, outward_normal)
        return rec


if __name__ == "__main__":
    s = Sphere(Point3(0, 0, 0), 1.5)
    print(f"center: {s.center}")
    print(f"radius: {s.radius}")
    assert s.center == Point3(0, 0, 0)
    assert s.radius == 1.5
    print(f"__repr__: {s!r}")
    assert eval(repr(s)) == s

    # hit 光线-球体相交检测
    # 沿 +z 方向、从原点射向球心在 (0,0,0)、半径 1 的球
    r_hit = Ray(Point3(0, 0, -5), Vec3(0, 0, 1))
    rec_hit = s.hit(r_hit)
    print(f"hit (命中): rec = {rec_hit}")
    assert rec_hit is not None
    assert abs(rec_hit.t - 3.5) < 1e-9  # 交点在 z = -5 + 3.5 = -1.5，距球心 1.5
    assert rec_hit.point == Point3(0, 0, -1.5)
    # 光线从球外射入，命中正面；法线应指向 ray 来的一侧（-z）
    assert rec_hit.front_face is True
    assert rec_hit.normal == Vec3(0, 0, -1)
    assert r_hit.direction.dot(rec_hit.normal) < 0

    # 完全错过球体（沿 +x 偏离）
    r_miss = Ray(Point3(5, 0, -5), Vec3(0, 0, 1))
    print(f"hit (未命中): {s.hit(r_miss)}")
    assert s.hit(r_miss) is None

    # t 区间限制：交点 t=3.5 落在 [0, 100) 内应命中
    assert s.hit(r_hit, 0.0, 100.0) is not None
    # 上界过小，两个根（3.5, 6.5）都被排除
    assert s.hit(r_hit, 0.0, 3.0) is None
    # 下界过大：近根 3.5 被排除，远根 6.5 仍落在区间内，应命中
    rec_far = s.hit(r_hit, 4.0, 100.0)
    assert rec_far is not None
    assert abs(rec_far.t - 6.5) < 1e-9
    # 下界更大：两个根都被排除
    assert s.hit(r_hit, 7.0, 100.0) is None

    # 光线从球内射出：命中的是背面，法线应翻转到朝向光线来的一侧
    r_inside = Ray(Point3(0, 0, 0), Vec3(0, 0, 1))
    rec_inside = s.hit(r_inside)
    assert rec_inside is not None
    assert rec_inside.front_face is False
    assert rec_inside.normal == Vec3(0, 0, -1)
    assert r_inside.direction.dot(rec_inside.normal) < 0

    print("\n所有测试通过")
