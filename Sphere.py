import math
from typing import override

from HitRecord import HitRecord
from Hittable import Hittable
from Interval import Interval
from Number import Number
from Point3 import Point3
from Ray import Ray
from Vec3 import Vec3


class Sphere(Hittable):
    """
    球体类

    一个球体由球心 center、半径 radius 与材质 material 定义。
    实现 Hittable 接口，提供光线-球体相交检测 hit()。
    """

    _center: Point3
    _radius: Number
    _material: Material

    def __init__(self, center: Point3, radius: Number, material: Material):
        """
        构造一个球体。

        Args:
            center (Point3): 球心坐标。
            radius (Number): 球的半径（float 或 int）。
            material (Material): 球体表面所用的材质。
        """
        self._center = center
        self._radius = radius
        self._material = material

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
        return f"Sphere(center={self._center!r}, radius={self._radius!r}, material={self._material!r})"

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
            ray_t: Interval = Interval(0.0, math.inf),
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
        若判别式 < 0 则无实交点，返回 None；否则依次检验两根是否落在区间
        ray_t（开区间）内，取落在区间内的最近交点 t，构造包含交点坐标 p、参数 t 的
        HitRecord，并用单位外法向量 outward_normal = (p - center) / radius
        调用 set_face_normal() 写入 front_face 与 normal（法线恒朝向光线来的一侧）。

        Args:
            ray (Ray): 待检测的光线。
            ray_t (Interval): 光线参数 t 的有效区间（开区间，不含端点），
                默认 Interval(0.0, +inf) 即 [0, +∞)。

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

        if not ray_t.surrounds(root):
            root = (h + sqrt_d) / a

            if not ray_t.surrounds(root):
                return None

        p: Point3 = ray.at(root)
        t: Number = root
        outward_normal: Vec3 = (p - self._center) / self._radius
        rec: HitRecord = HitRecord(p, outward_normal, t)
        rec.set_face_normal(ray, outward_normal)
        rec.material = self._material
        return rec


