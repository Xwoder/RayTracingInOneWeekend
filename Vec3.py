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

    @property
    def x(self) -> Number:
        """
        向量的 x 分量（只读属性）。

        Returns:
            Number: x 轴方向的分量
        """
        return self._x

    @property
    def y(self) -> Number:
        """
        向量的 y 分量（只读属性）。

        Returns:
            Number: y 轴方向的分量
        """
        return self._y

    @property
    def z(self) -> Number:
        """
        向量的 z 分量（只读属性）。

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

    def __add__(self, other: "Vec3") -> "Vec3":
        """
        向量加法（v + u），返回新向量（对应 C++ 的 operator+）。
        不修改原向量。

        Args:
            other (Vec3): 被加的向量。

        Returns:
            Vec3: 分量相加后的新向量
        """
        return Vec3(self._x + other.x, self._y + other.y, self._z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        """
        向量减法（v - u），返回新向量（对应 C++ 的 operator-）。
        不修改原向量。

        Args:
            other (Vec3): 被减的向量。

        Returns:
            Vec3: 分量相减后的新向量
        """
        return Vec3(self._x - other.x, self._y - other.y, self._z - other.z)

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
            return Vec3(self._x * other.x, self._y * other.y, self._z * other.z)
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
            return Vec3(self._x / other.x, self._y / other.y, self._z / other.z)
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
        return self._x == other.x and self._y == other.y and self._z == other.z

    def length_squared(self) -> float:
        """
        计算向量长度的平方（模的平方），即 x² + y² + z²。
        对应 C++ 的 length_squared()。

        Returns:
            float: 各分量平方和
        """
        return self._x ** 2 + self._y ** 2 + self._z ** 2

    def length(self) -> float:
        """
        计算向量的欧几里得长度（模），即 sqrt(length_squared())。
        对应 C++ 的 length()（内部委托给 length_squared()）。

        Returns:
            float: 向量各分量平方和的算术平方根
        """
        return math.sqrt(self.length_squared())

    def dot(self, other: "Vec3") -> Number:
        """
        向量内积（点积），返回标量。
        对应 C++ 的 dot(const vec3&, const vec3&)。

        Args:
            other (Vec3): 另一个向量。

        Returns:
            Number: 各分量乘积之和（x1*x2 + y1*y2 + z1*z2）
        """
        return self._x * other.x + self._y * other.y + self._z * other.z

    def normalized(self) -> "Vec3":
        """
        返回当前向量的单位向量（方向相同、长度为 1）。
        实现为 self / self.length()，不修改原向量（对应 C++ 的 unit_vector）。
        注意：若向量长度为零，将触发除零错误（ZeroDivisionError）。

        Returns:
            Vec3: 归一化后的新向量
        """
        return self / self.length()

    def __repr__(self) -> str:
        """
        返回向量的官方字符串表示，形如 Vec3(x, y, z)。
        供 repr()、交互式解释器及调试使用；其输出应满足 eval(repr(v))
        可还原出等价对象。

        Returns:
            str: 包含三个分量的字符串表示
        """
        return f"Vec3({self._x}, {self._y}, {self._z})"

    def cross(self, other: "Vec3") -> "Vec3":
        """
        向量叉积（外积），返回一个与 self 和 other 都垂直的新向量。
        对应 C++ 的 cross(const vec3&, const vec3&)。
        结果方向由右手定则确定，长度等于 |self| * |other| * sin(theta)
        （即两向量张成平行四边形的面积）。

        Args:
            other (Vec3): 另一个向量。

        Returns:
            Vec3: 叉积得到的新向量
        """
        return Vec3(
            self._y * other.z - self._z * other.y,
            self._z * other.x - self._x * other.z,
            self._x * other.y - self._y * other.x,
        )


Point3 = Vec3
Color = Vec3

if __name__ == '__main__':
    v = Vec3(3, 4, 5)
    s1 = Vec3.from_sequence([1, 2, 3])
    s2 = Vec3.from_sequence((1, 2, 3))

    print(v.x, v.y, v.z)
    print(f"{v.length() = }")

    print(s1.x, s1.y, s1.z)
    print(s2.x, s2.y, s2.z)
