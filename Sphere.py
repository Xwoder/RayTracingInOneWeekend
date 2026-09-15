import math

from Number import Number
from Ray import Ray
from Vec3 import Point3, Vec3


class Sphere:
    """
    球体类

    一个球体由球心 center 与半径 radius 定义。
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

    def hit(self, r: Ray) -> Number:
        """
        判断光线是否击中本球体，并返回最近的正向交点参数 t。

        对应 C++ 的 hit_sphere（升级版）。求解球面方程
        |P(t) - center|² = radius² 的展开式 a·t² + b·t + c = 0，其中：
            oc      = center - origin
            a       = dot(dir, dir)
            b       = -2·dot(dir, oc)
            c       = dot(oc, oc) - radius²
            discriminant = b² - 4·a·c
        若判别式 < 0 则无实交点，返回 None；否则返回较小的正根
        (-b - sqrt(discriminant)) / (2·a)（取离光线原点更近的交点）。

        Args:
            r (Ray): 待检测的光线。

        Returns:
            float | None: 最近正向交点的参数 t；光线未击中球体时返回 None。
        """
        oc: Vec3 = self._center - r.origin
        a: Number = r.direction.dot(r.direction)
        b: Number = -2.0 * r.direction.dot(oc)
        c: Number = oc.dot(oc) - self._radius * self._radius
        discriminant: Number = b * b - 4.0 * a * c
        if discriminant < 0:
            return None

        return (-b - math.sqrt(discriminant)) / (2.0 * a)


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
    t = s.hit(r_hit)
    print(f"hit (命中): t = {t}")
    assert t is not None
    assert abs(t - 3.5) < 1e-9  # 交点在 z = -5 + 3.5 = -1.5，距球心 1.5

    # 完全错过球体（沿 +x 偏离）
    r_miss = Ray(Point3(5, 0, -5), Vec3(0, 0, 1))
    print(f"hit (未命中): {s.hit(r_miss)}")
    assert s.hit(r_miss) is None

    print("\n所有测试通过！")
