# Ray Tracing in One Weekend - image gradient (Python port)

import sys


def main() -> None:
    # Image
    image_width = 256
    image_height = 256

    # Render
    out_std = sys.stdout
    out_std.write(f"P3\n{image_width} {image_height}\n255\n")

    out_err = sys.stderr

    for row in range(image_height):
        out_err.write(f"Rendering row {row}\n")
        for col in range(image_width):
            r = col / (image_width - 1)
            g = row / (image_height - 1)
            b = 0.0

            ir = int(255 * r)
            ig = int(255 * g)
            ib = int(255 * b)

            out_std.write(f"{ir} {ig} {ib}\n")
    out_std.write("Done")


if __name__ == "__main__":
    main()
