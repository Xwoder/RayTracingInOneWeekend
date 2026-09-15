from typing import TextIO

from Vec3 import Vec3

Color = Vec3


def write_color(out: TextIO, pixel_color: Color) -> None:
    r = pixel_color.x
    g = pixel_color.y
    b = pixel_color.z

    rbyte = int(255 * r)
    gbyte = int(255 * g)
    bbyte = int(255 * b)

    out.write(f"{rbyte} {gbyte} {bbyte}\n")


if __name__ == '__main__':
    import sys

    color = Color(1.0, 0.5, 0.25)

    write_color(sys.stdout, color)
