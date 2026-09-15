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

    def __getitem__(self, i: int) -> Number:
        """
        下标访问运算符（v[i]），返回第 i 个分量。
        对应 C++ 的 double operator[](int i) const。

        Args:
            i (int): 分量索引，0 表示 x，1 表示 y，2 表示 z。

        Returns:
            Number: 对应的分量值

        Raises:
            IndexError: 当索引不在 0~2 范围内时抛出
        """
        if i == 0:
            return self._x
        if i == 1:
            return self._y
        if i == 2:
            return self._z
        raise IndexError("Vec3 index out of range")

    def __iadd__(self, other: "Vec3") -> "Vec3":
        """
        原地加法赋值运算符（v += u），将自身各分量加上 other 的对应分量，
        并返回自身（对应 C++ 的 vec3& operator+=(const vec3& v)）。

        Args:
            other (Vec3): 加到自身的另一个向量。

        Returns:
            Vec3: 自身（已就地修改）
        """
        self._x += other.x()
        self._y += other.y()
        self._z += other.z()
        return self

    def __isub__(self, other: "Vec3") -> "Vec3":
        """
        原地减法赋值运算符（v -= u），将自身各分量减去 other 的对应分量，
        并返回自身（对应 C++ 的 vec3& operator-=(const vec3& v)）。

        Args:
            other (Vec3): 被减的向量。

        Returns:
            Vec3: 自身（已就地修改）
        """
        self._x -= other.x()
        self._y -= other.y()
        self._z -= other.z()
        return self

    def __imul__(self, other: "Vec3 | Number") -> "Vec3":
        """
        原地乘法赋值运算符（v *= t 或 v *= u），就地修改自身各分量，
        并返回自身（对应 C++ 的 vec3& operator*=(double t)）。
        - 标量 t：各分量乘以 t。
        - 向量 u：逐分量相乘（Hadamard 积）。

        Args:
            other (Vec3 | Number): 右侧操作数，可为标量或向量。

        Returns:
            Vec3: 自身（已就地修改）
        """
        if isinstance(other, Vec3):
            self._x *= other.x()
            self._y *= other.y()
            self._z *= other.z()
        else:
            self._x *= other
            self._y *= other
            self._z *= other
        return self

    def __add__(self, other: "Vec3") -> "Vec3":
        """
        向量加法（v + u），返回新向量（对应 C++ 的 operator+）。
        不修改原向量。

        Args:
            other (Vec3): 被加的向量。

        Returns:
            Vec3: 分量相加后的新向量
        """
        return Vec3(self._x + other.x(), self._y + other.y(), self._z + other.z())

    def __sub__(self, other: "Vec3") -> "Vec3":
        """
        向量减法（v - u），返回新向量（对应 C++ 的 operator-）。
        不修改原向量。

        Args:
            other (Vec3): 被减的向量。

        Returns:
            Vec3: 分量相减后的新向量
        """
        return Vec3(self._x - other.x(), self._y - other.y(), self._z - other.z())

    def __mul__(self, other: "Vec3 | Number") -> "Vec3":
        """
        乘法（v * t 或 v * u），返回新向量，不修改原向量。
        - 标量 t：各分量乘以 t（对应 C++ 的 operator*(double)）。
        - 向量 u：逐分量相乘（Hadamard 积）。

        Args:
            other (Vec3 | Number): 右侧操作数，可为标量或向量。

        Returns:
            Vec3: 相乘后的新向量
        """
        if isinstance(other, Vec3):
            return Vec3(self._x * other.x(), self._y * other.y(), self._z * other.z())
        return Vec3(self._x * other, self._y * other, self._z * other)

    def __rmul__(self, other: "Number") -> "Vec3":
        """
        右乘（t * v），使标量可写在左侧。直接复用 __mul__。

        Args:
            other (Number): 左侧的标量。

        Returns:
            Vec3: 相乘后的新向量
        """
        return self.__mul__(other)

    def __truediv__(self, other: "Vec3 | Number") -> "Vec3":
        """
        除法（v / t 或 v / u），返回新向量，不修改原向量。
        - 标量 t：各分量除以 t（对应 C++ 的 operator/(double)）。
        - 向量 u：逐分量相除。

        Args:
            other (Vec3 | Number): 右侧操作数，可为标量或向量。

        Returns:
            Vec3: 相除后的新向量
        """
        if isinstance(other, Vec3):
            return Vec3(self._x / other.x(), self._y / other.y(), self._z / other.z())
        return Vec3(self._x / other, self._y / other, self._z / other)

    def __eq__(self, other: object) -> bool:
        """
        相等判断（v == u），当三个分量都相等时返回 True。
        对应 C++ 的 operator==。若 other 不是 Vec3，则返回 NotImplemented
        交由 Python 处理（通常得到 False）。

        Args:
            other (object): 比较对象。

        Returns:
            bool: 分量是否全部相等
        """
        if not isinstance(other, Vec3):
            return NotImplemented
        return self._x == other.x() and self._y == other.y() and self._z == other.z()

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
