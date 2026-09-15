import math
from typing import Sequence

type Number = float | int


class Vec3:
    _x: Number
    _y: Number
    _z: Number

    def __init__(self,
                 x: Number = 0,
                 y: Number = 0,
                 z: Number = 0):
        """
        初始化三维向量，使用给定的三个分量设置 x、y、z 坐标。

        Args:
            x (Number): x 轴方向的分量，取值类型为 float 或 int。
            y (Number): y 轴方向的分量，取值类型为 float 或 int。
            z (Number): z 轴方向的分量，取值类型为 float 或 int。
        """

        self._x = x
        self._y = y
        self._z = z

    @classmethod
    def from_sequence(cls, value: Sequence[Number]):
        """
        从包含三个分量的序列构造 Vec3 实例

        Args:
            value (Sequence[Number]): 包含三个数值分量的序列（如列表或元组）

        Returns:
            Vec3: 由序列中三个分量依次作为 x、y、z 构造的向量实例

        Raises:
            ValueError: 当序列长度不等于 3 时抛出
        """

        if len(value) != 3:
            raise ValueError("Vec3 requires exactly 3 values")

        x = value[0]
        y = value[1]
        z = value[2]

        return cls(x, y, z)

    def x(self) -> Number:
        """
        获取向量的 x 分量。

        Returns:
            Number: x 轴方向的分量
        """
        return self._x

    def y(self) -> Number:
        """
        获取向量的 y 分量。

        Returns:
            Number: y 轴方向的分量
        """
        return self._y

    def z(self) -> Number:
        """
        获取向量的 z 分量。

        Returns:
            Number: z 轴方向的分量
        """
        return self._z

    def __neg__(self) -> "Vec3":
        """
        一元负号运算符（-v），返回各分量取反的新向量。
        对应 C++ 的 vec3 operator-() const。

        Returns:
            Vec3: 各分量取反后的新向量
        """
        return Vec3(-self._x, -self._y, -self._z)

    def length(self):
        """
        计算向量的欧几里得长度（模）

        Returns:
            float: 向量各分量平方和的算术平方根，即 sqrt(x² + y² + z²)
        """
        return math.sqrt(
            self._x ** 2 +
            self._y ** 2 +
            self._z ** 2
        )


Point3 = Vec3
Color = Vec3

if __name__ == '__main__':
    v = Vec3(3, 4, 5)
    s1 = Vec3.from_sequence([1, 2, 3])
    s2 = Vec3.from_sequence((1, 2, 3))

    print(v.x(), v.y(), v.z())
    print(f"{v.length() = }")

    print(s1.x(), s1.y(), s1.z())
    print(s2.x(), s2.y(), s2.z())
