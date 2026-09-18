# Ray Tracing in One Weekend

A ray tracing renderer written in Python, built step by step following the classic
[*Ray Tracing in One Weekend*](https://raytracing.github.io/books/RayTracingInOneWeekend.html)
tutorial. The current stage supports: camera viewport and pixel grid, ray-sphere
intersection, a material system (Lambertian / Metal / Dielectric), physically based
shading with recursive light bounces (`max_depth`), sky-gradient background, and
antialiasing with multiple samples.

## Features

- **Vector and geometry math**: `Vec3` provides addition / subtraction / scalar
  multiplication / dot product / cross product / unit vector operations.
- **Camera model**: `Camera` encapsulates the viewport, pixel deltas and rendering
  logic, following the `camera` chapter of the book. It supports per-ray shading,
  multi-bounce recursion (`max_depth`) and antialiased sampling.
- **Sphere intersection**: `Sphere.hit()` solves the ray-sphere equation with the
  discriminant method and returns the nearest hit.
- **Material system**: `material.Material` is an abstract base class whose `scatter`
  returns `(attenuation, scattered_ray)` on a bounce or `None` when the ray is
  absorbed. Three concrete materials are provided:
  - **Lambertian** (`material.Lambertian`): ideal diffuse reflection. Scatters into
    the hemisphere around the surface normal with cosine weighting; attenuation is
    the surface `albedo`.
  - **Metal** (`material.Metal`): specular reflection with adjustable `fuzz` (clamped
    to `[0,1]`) for frosted/blurry mirrors. Returns `None` when the perturbed
    reflection points into the surface (ray absorbed).
  - **Dielectric** (`material.Dielectric`): transparent refraction (e.g. glass) with
    total internal reflection and Schlick-approximation Fresnel reflection;
    attenuation is pure white.
- **Sky-gradient background**: on miss, interpolates a blue-white gradient by the
  ray direction's y component.
- **Antialiasing**: each pixel is randomly jittered and sampled multiple times
  (`samples_per_pixel`) then averaged.

## Project Structure

```
.
├── main.py            # Entry point: build scene (ground + Lambertian/Metal/Dielectric spheres) and call camera.render()
├── Camera.py          # Camera: rendering, viewport math, per-ray shading, antialiased sampling, multi-bounce
├── Sphere.py          # Sphere: implements Hittable, ray-sphere intersection
├── Hittable.py        # Abstract base class (ABC) for hittable objects
├── HittableList.py    # Scene container: aggregates objects, returns the nearest hit
├── HitRecord.py       # Hit record: point / normal / t / front_face / material
├── Ray.py             # Ray: origin + direction
├── Vec3.py            # 3D vector (mutable components, read-only x/y/z properties)
├── Point3.py          # 3D point (frozen dataclass)
├── Color.py           # Color and write_color (PPM output)
├── Interval.py        # Interval: clamps the valid t range of a ray
├── Number.py          # Numeric type alias (float | int)
├── Random.py          # Random number utilities
├── material/          # Material subsystem (shading logic)
│   ├── Material.py    #   Abstract base: scatter() -> (attenuation, scattered) | None
│   ├── Lambertian.py  #   Ideal diffuse (albedo)
│   ├── Metal.py       #   Specular reflection with fuzz
│   ├── Dielectric.py  #   Refraction + Fresnel (Schlick) reflection
│   └── __init__.py
├── draw_image.sh      # Convenience script: run main.py and open the timestamped image.PPM
└── image_*.PPM        # Rendered output(s)
```

## Requirements

- Python `>= 3.14`
- Dependencies: `matplotlib`, `numpy`, `pillow` (managed via `uv`, see `pyproject.toml`)

## Running

Use the bundled script (requires [uv](https://docs.astral.sh/uv/) installed):

```bash
./draw_image.sh
```

This runs `main.py`, writes the PPM image to a timestamped file `image_<YYYY_MM_DD_HH_MM_SS>.PPM`
and opens it for preview.

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
uv run python material/Lambertian.py
uv run python material/Metal.py
uv run python material/Dielectric.py
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
