from typing import TextIO

from Interval import Interval
from Vec3 import Vec3

Color = Vec3

# 对应 C++ 中的 static const interval intensity(0.000, 0.999)
intensity = Interval(0, 1)


def write_color(out: TextIO, pixel_color: Color) -> None:
    r = pixel_color.x
    g = pixel_color.y
    b = pixel_color.z

    # 将 [0,1] 分量映射到字节范围 [0,255]（含钳制）
    rbyte = int(255 * intensity.clamp(r))
    gbyte = int(255 * intensity.clamp(g))
    bbyte = int(255 * intensity.clamp(b))

    out.write(f"{rbyte} {gbyte} {bbyte}\n")


if __name__ == '__main__':
    import sys

    color = Color(1.0, 0.5, 0.25)
    write_color(sys.stdout, color)

    color = Color(1.1, 0.5, 0.25)
    write_color(sys.stdout, color)
