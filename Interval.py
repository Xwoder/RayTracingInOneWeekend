import math
from typing import Self

from Number import Number


class Interval:
    """
    区间（标量闭/开区间）类

    对应《Ray Tracing in One Weekend》的 interval 工具类，用于描述光线
    参数 t 的有效取值范围等一维区间。区间由下界 min 与上界 max 定义：

    - 默认构造（min=+inf, max=-inf）表示一个“空区间”（上界小于下界）。
    - interval(min, max) 构造一个普通区间。

    提供：
    - size()：区间长度。
    - contains(x)：x 是否落在闭区间 [min, max] 内。
    - surrounds(x)：x 是否落在开区间 (min, max) 内（对应光线 t 的搜索区间）。
    - 两个静态成员 empty（空区间）与 universe（全空间 [-inf, +inf]）。
    """

    _min: Number
    _max: Number

    def __init__(self,
                 min_value: Number = math.inf,
                 max_value: Number = -math.inf):
        """
        构造一个区间。

        - 不传参（或只传一个参数未覆盖的情况）时，默认 min=+inf、max=-inf，
          得到“空区间”（与 C++ 默认构造函数等价）。
        - 传入 (min, max) 时构造普通区间（与 C++ 带参构造函数等价）。

        Args:
            min_value (Number): 区间下界，默认正无穷。
            max_value (Number): 区间上界，默认负无穷。
        """
        self._min = min_value
        self._max = max_value

    @property
    def min(self) -> Number:
        """返回区间下界（对应 C++ 的 min 成员）。"""
        return self._min

    @property
    def max(self) -> Number:
        """返回区间上界（对应 C++ 的 max 成员）。"""
        return self._max

    def size(self) -> Number:
        """
        返回区间长度（max - min）。

        Returns:
            Number: 区间上界与下界之差。
        """
        return self._max - self._min

    def contains(self, x: Number) -> bool:
        """
        判断 x 是否落在闭区间 [min, max] 内（包含端点）。

        Args:
            x (Number): 待检测的标量。

        Returns:
            bool: 当 min <= x <= max 时返回 True，否则 False。
        """
        return self._min <= x <= self._max

    def surrounds(self, x: Number) -> bool:
        """
        判断 x 是否落在开区间 (min, max) 内（不含端点）。

        光线求交时通常用它来判断参数 t 是否落在有效搜索区间内
        （对应 C++ 的 surrounds，不含端点）。

        Args:
            x (Number): 待检测的标量。

        Returns:
            bool: 当 min < x < max 时返回 True，否则 False。
        """
        return self._min < x < self._max

    def __repr__(self) -> str:
        """
        返回区间的官方字符串表示，形如 Interval(min, max)。
        其输出应满足 eval(repr(i)) 可还原出等价对象。

        Returns:
            str: 包含下界与上界的字符串表示。
        """
        return f"Interval({self._min}, {self._max})"

    def __eq__(self, other: object) -> bool:
        """
        相等判断（i == j），当下界与上界分别相等时返回 True。
        若 other 不是 Interval，则返回 NotImplemented。

        Args:
            other (object): 比较对象。

        Returns:
            bool: 下界与上界是否全部相等。
        """
        if not isinstance(other, Interval):
            return NotImplemented
        return self._min == other.min and self._max == other.max


# 静态成员（对应 C++ 的 interval::empty 与 interval::universe）
Interval.empty = Interval(math.inf, -math.inf)     # 空区间
Interval.universe = Interval(-math.inf, math.inf)  # 全空间


if __name__ == "__main__":
    # 默认构造：空区间
    e = Interval()
    print(f"default(empty): {e}")
    assert e == Interval.empty
    # 空区间 min=+inf, max=-inf，size = max - min = -inf - (+inf) = -inf
    assert e.size() == -math.inf
    assert not e.contains(0.0)
    assert not e.surrounds(0.0)

    # 带参构造普通区间
    i = Interval(3.0, 10.0)
    print(f"Interval(3, 10): {i}")
    assert i.min == 3.0
    assert i.max == 10.0
    assert i.size() == 7.0

    # contains：闭区间含端点
    assert i.contains(3.0)
    assert i.contains(10.0)
    assert i.contains(5.0)
    assert not i.contains(2.0)
    assert not i.contains(11.0)

    # surrounds：开区间不含端点
    assert i.surrounds(5.0)
    assert not i.surrounds(3.0)
    assert not i.surrounds(10.0)
    assert not i.surrounds(2.0)

    # 静态成员
    print(f"empty: {Interval.empty}")
    print(f"universe: {Interval.universe}")
    assert Interval.empty.min == math.inf
    assert Interval.empty.max == -math.inf
    assert Interval.universe.min == -math.inf
    assert Interval.universe.max == math.inf
    assert Interval.universe.contains(0.0)
    assert Interval.universe.surrounds(0.0)
    assert Interval.universe.surrounds(-1e9)
    assert Interval.universe.surrounds(1e9)

    # __repr__ 可还原
    print(f"__repr__: {i!r}")
    assert eval(repr(i)) == i

    print("\n所有测试通过")
