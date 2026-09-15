# Ray Tracing in One Weekend - image gradient (Python port)

import sys

from Camera import Camera
from Color import Color, write_color
from Ray import Ray
from Vec3 import Vec3


def ray_color(r: Ray):
    unit_direction = r.direction.unit_vector()
    a = (unit_direction.y + 1.0) / 2
    return (1.0 - a) * Color(1.0, 1.0, 1.0) + a * Color(0.5, 0.7, 1.0)


def main() -> None:
    # Image
    aspect_ratio = 16.0 / 9.0
    image_width = 400

    # Calculate the image height, and ensure that it's at least 1.
    image_height = int(image_width / aspect_ratio)
    image_height = 1 if image_height < 1 else image_height

    # Camera
    camera = Camera()
    focal_length = 1.0
    focal_direction = Vec3(0, 0, focal_length)

    # Viewport widths less than one are ok since they are real valued.
    viewport_height = 2.0
    viewport_width = viewport_height * (image_width / image_height)

    # Calculate the vectors across the horizontal and down the vertical viewport edges.
    viewport_u: Vec3 = Vec3(viewport_width, 0, 0)
    viewport_v: Vec3 = Vec3(0, -viewport_height, 0)

    # Calculate the horizontal and vertical delta vectors from pixel to pixel.
    pixel_delta_u: Vec3 = viewport_u / image_width
    pixel_delta_v: Vec3 = viewport_v / image_height

    # Calculate the location of the upper left pixel.
    viewport_upper_left = camera.position - focal_direction - viewport_u / 2 - viewport_v / 2
    pixel00_loc = viewport_upper_left + (pixel_delta_u + pixel_delta_v) / 2

    # Render
    out_std = sys.stdout
    out_std.write(f"P3\n{image_width} {image_height}\n255\n")

    out_err = sys.stderr

    for row in range(image_height):
        out_err.write(f"Rendering row {row}\n")
        for col in range(image_width):
            # r = col / (image_width - 1)
            # g = row / (image_height - 1)
            # b = 0.0
            # pixel_color = Color(r, g, b)
            pixel_center = pixel00_loc + (col * pixel_delta_u) + (row * pixel_delta_v)
            ray_direction = pixel_center - camera.position
            r = Ray(camera.position, ray_direction)
            pixel_color = ray_color(r)
            write_color(out_std, pixel_color)
    out_std.write("Done")


if __name__ == "__main__":
    main()
