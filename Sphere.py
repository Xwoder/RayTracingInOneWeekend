from Number import Number
from Vec3 import Point3


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


if __name__ == "__main__":
    s = Sphere(Point3(0, 0, 0), 1.5)
    print("center:", s.center)
    print("radius:", s.radius)
    assert s.center == Point3(0, 0, 0)
    assert s.radius == 1.5
    print("__repr__:", repr(s))
    assert eval(repr(s)) == s
    print("\n所有测试通过！")
