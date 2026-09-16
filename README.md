# Ray Tracing in One Weekend

A ray tracing renderer written in Python, built step by step following the classic
[*Ray Tracing in One Weekend*](https://raytracing.github.io/books/RayTracingInOneWeekend.html)
tutorial. The current stage supports: camera viewport and pixel grid, ray-sphere
intersection, normal-shaded visualization, sky-gradient background, and antialiasing
with multiple samples.

## Features

- **Vector and geometry math**: `Vec3` provides addition / subtraction / scalar
  multiplication / dot product / cross product / unit vector operations.
- **Camera model**: `Camera` encapsulates the viewport, pixel deltas and rendering
  logic, following the `camera` chapter of the book.
- **Sphere intersection**: `Sphere.hit()` solves the ray-sphere equation with the
  discriminant method and returns the nearest hit.
- **Normal visualization**: on hit, shades with the unit normal mapped as
  `0.5 * (N + 1)` so the geometry is directly visible.
- **Sky-gradient background**: on miss, interpolates a blue-white gradient by the
  ray direction's y component.
- **Antialiasing**: each pixel is randomly jittered and sampled multiple times
  (`samples_per_pixel`) then averaged.

## Project Structure

```
.
├── main.py            # Entry point: build scene (small sphere + ground) and call camera.render()
├── Camera.py          # Camera: rendering, viewport math, per-ray shading, antialiased sampling
├── Sphere.py          # Sphere: implements Hittable, ray-sphere intersection
├── Hittable.py        # Abstract base class (ABC) for hittable objects
├── HittableList.py    # Scene container: aggregates objects, returns the nearest hit
├── HitRecord.py       # Hit record: point / normal / t / front_face
├── Ray.py             # Ray: origin + direction
├── Vec3.py            # 3D vector (mutable components, read-only x/y/z properties)
├── Point3.py          # 3D point (frozen dataclass)
├── Color.py           # Color and write_color (PPM output)
├── Interval.py        # Interval: clamps the valid t range of a ray
├── Number.py          # Numeric type alias (float | int)
├── Random.py          # Random number utilities
├── draw_image.sh      # Convenience script: run main.py and open image.PPM
└── image.PPM          # Rendered output
```

## Requirements

- Python `>= 3.14`
- Dependencies: `matplotlib`, `pillow` (managed via `uv`, see `pyproject.toml`)

## Running

Use the bundled script (requires [uv](https://docs.astral.sh/uv/) installed):

```bash
./draw_image.sh
```

This runs `main.py`, writes the PPM image to `image.PPM` and opens it for preview.

You can also run it manually:

```bash
uv run python main.py > image.PPM
```

Render progress is printed to standard error (stderr); the PPM image stream goes to
standard output (stdout).

## Self-tests

Each core module file has a `__main__` self-test block (print + assert) at the
bottom. Run the file directly to verify it:

```bash
uv run python Vec3.py
uv run python Sphere.py
uv run python Camera.py
# ... and so on
```

On success it prints "所有测试通过" (all tests passed).

## Rendering Principle (Brief)

1. `Camera` computes, in `initialize()`, the image height, viewport size and pixel
   deltas from `aspect_ratio` and `image_width`; the camera sits at the origin looking
   down -Z.
2. For each pixel `(i, j)`, it shoots `samples_per_pixel` randomly jittered rays
   (`get_ray` + `sample_square`) for antialiasing.
3. `ray_color` tests the scene along the ray: on hit it returns the normal shading
   `0.5 * (N + 1)`; on miss it returns the sky-gradient background.
4. After averaging the multiple samples, it writes the result in PPM (P3) format via
   `write_color`.

## License

This project is for learning purposes and follows the open spirit of the original
tutorial.
