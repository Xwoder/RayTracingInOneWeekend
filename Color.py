import math
from typing import TextIO

from Interval import Interval
from Number import Number
from Vec3 import Vec3

Color = Vec3

# 对应 C++ 中的 static const interval intensity(0.000, 0.999)
intensity = Interval(0, 1)


def linear_to_gamma(linear_component: Number) -> Number:
    if linear_component > 0:
        return math.sqrt(linear_component)
    else:
        return 0.0


def write_color(out: TextIO, pixel_color: Color) -> None:
    r = pixel_color.x
    g = pixel_color.y
    b = pixel_color.z

    # 对线性分量做伽马校正（gamma 2）
    r = linear_to_gamma(r)
    g = linear_to_gamma(g)
    b = linear_to_gamma(b)

    # 将 [0,1] 分量映射到字节范围 [0,255]（含钳制）
    rbyte = int(255 * intensity.clamp(r))
    gbyte = int(255 * intensity.clamp(g))
    bbyte = int(255 * intensity.clamp(b))

    out.write(f"{rbyte} {gbyte} {bbyte}\n")


