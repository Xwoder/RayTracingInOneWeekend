from Vec3 import Point3, Vec3


class Ray:
    """
    光线类

    一条光线由原点 orig 与方向 dir 定义，参数方程 P(t) = orig + t * dir。
    """
    _orig: Point3
    _dir: Vec3

    def __init__(self, origin: Point3, direction: Vec3):
        """
        构造一条光线。

        Args:
            origin (Point3): 光线的起点。
            direction (Vec3): 光线的方向（无需单位化，由调用方决定）。
        """
        self._orig = origin
        self._dir = direction

    @property
    def origin(self) -> Point3:
        """返回光线原点（对应 C++ const point3& origin()）。"""
        return self._orig

    @property
    def direction(self) -> Vec3:
        """返回光线方向（对应 C++ const vec3& direction()）。"""
        return self._dir

    def at(self, t: float) -> Point3:
        """
        计算光线在参数 t 处的位置（对应 C++ point3 at(double t)）。

        Args:
            t (float): 参数值，t >= 0 表示沿光线方向前进。

        Returns:
            Point3: 位置 orig + t*dir。
        """
        return self._orig + t * self._dir


if __name__ == "__main__":
    r = Ray(Point3(0, 0, 0), Vec3(1, 2, 3))
    print(f"origin: {r.origin}")
    print(f"direction: {r.direction}")
    print(f"at(0): {r.at(0)}")
    print(f"at(1): {r.at(1)}")
    print(f"at(2.5): {r.at(2.5)}")
    assert r.at(0) == Point3(0, 0, 0)
    assert r.at(1) == Point3(1, 2, 3)
    assert r.at(2.5) == Point3(2.5, 5.0, 7.5)
    print("\n所有测试通过！")
