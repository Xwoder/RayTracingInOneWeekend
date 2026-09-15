import math
from typing import Sequence

type Number = float | int


class Vec3:
    x: Number
    y: Number
    z: Number

    def __init__(self,
                 x: Number,
                 y: Number,
                 z: Number):
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
        if len(value) != 3:
            raise ValueError("Vec3 requires exactly 3 values")

        x = value[0]
        y = value[1]
        z = value[2]

        return cls(x, y, z)

    def length(self):
        return math.sqrt(
            self.x ** 2 +
            self.y ** 2 +
            self.z ** 2
        )


if __name__ == '__main__':
    v = Vec3(1, 2, 3)
    s1 = Vec3.from_sequence([1,2,3])
    s2 = Vec3.from_sequence((1,2,3))

    print(v.x, v.y, v.z)
    print(v.length())

    print(s1.x, s1.y, s1.z)
    print(s2.x, s2.y, s2.z)
