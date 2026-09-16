from Point3 import Point3
from Vec3 import  Vec3


class Camera:
    """
    相机类

    用位置 position 与朝向 direction 描述一台相机。
    位置默认在三维直角坐标系的原点，朝向默认沿 Z 轴正方向。
    """
    _position: Point3
    _direction: Vec3

    def __init__(self,
                 position: Point3 = Point3(0, 0, 0),
                 direction: Vec3 = Vec3(0, 0, 1)):
        """
        构造一台相机。

        Args:
            position (Point3 | None): 相机位置，默认在原点 (0, 0, 0)。
            direction (Vec3 | None): 相机朝向，默认沿 Z 轴正方向 (0, 0, 1)。
        """
        self._position = position
        self._direction = direction

    @property
    def position(self) -> Point3:
        """返回相机位置（默认在原点）。"""
        return self._position

    @property
    def direction(self) -> Vec3:
        """返回相机朝向（默认沿 Z 轴正方向）。"""
        return self._direction


if __name__ == "__main__":
    # 默认构造：位于原点，朝向 +Z
    c = Camera()
    print(f"default position: {c.position}")
    print(f"default direction: {c.direction}")
    assert c.position == Point3(0, 0, 0)
    assert c.direction == Vec3(0, 0, 1)

    # 自定义构造
    c2 = Camera(Point3(1, 2, 3), Vec3(0, 1, 0))
    print(f"custom position: {c2.position}")
    print(f"custom direction: {c2.direction}")
    assert c2.position == Point3(1, 2, 3)
    assert c2.direction == Vec3(0, 1, 0)

    print("\n所有测试通过！")
