import math
from typing import Sequence

type Number = float | int


class Vec3:
    x: Number
    y: Number
    z: Number

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

        self.x = x
        self.y = y
        self.z = z

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

    def length(self):
        """
        计算向量的欧几里得长度（模）

        Returns:
            float: 向量各分量平方和的算术平方根，即 sqrt(x² + y² + z²)
        """
        return math.sqrt(
            self.x ** 2 +
            self.y ** 2 +
            self.z ** 2
        )


if __name__ == '__main__':
    v = Vec3(3, 4, 5)
    s1 = Vec3.from_sequence([1, 2, 3])
    s2 = Vec3.from_sequence((1, 2, 3))

    print(v.x, v.y, v.z)
    print(f"{v.length() = }")

    print(s1.x, s1.y, s1.z)
    print(s2.x, s2.y, s2.z)
