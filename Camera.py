import math
import sys
from typing import TextIO

from Color import Color, write_color
from HitRecord import HitRecord
from Hittable import Hittable
from Interval import Interval
from Point3 import Point3
from Ray import Ray
from Vec3 import Vec3


class Camera:
    """
    相机类（参考《Ray Tracing in One Weekend》的 camera 实现）

    封装渲染一帧所需的所有参数与逻辑：

    - 公共参数：aspect_ratio（宽高比）、image_width（像素宽度）。
    - render(world, out)：按 PPM 格式输出图像。
    - 私有状态：image_height、center、pixel00_loc、pixel_delta_u、
      pixel_delta_v，由 initialize() 根据公共参数计算。
    - ray_color(r, world)：对单条光线着色（命中物体用法线映射，
      否则返回天空渐变背景）。

    对应 C++ 的：
        class camera {
          public:
            double aspect_ratio = 1.0;
            int    image_width  = 100;
            void render(const hittable& world);
          private:
            void initialize();
            color ray_color(const ray& r, const hittable& world) const;
        };
    """

    def __init__(self,
                 aspect_ratio: float = 1,
                 image_width: int = 400):
        """
        构造一台相机。

        Args:
            aspect_ratio (float): 图像宽高比（宽度 / 高度），默认 1.0。
            image_width (int): 渲染图像的像素宽度，默认 100。
        """
        self._aspect_ratio = aspect_ratio
        self._image_width = image_width

    def render(self,
               world: Hittable,
               out: TextIO = sys.stdout) -> None:
        """
        渲染场景 world 并将结果以 PPM（P3）格式写入 out。

        对应 C++ camera::render：先 initialize() 计算相机与视口，
        再逐像素发射光线并着色。进度信息写入标准错误（对应 std::clog）。

        Args:
            world (Hittable): 待渲染的场景（可命中物体）。
            out (TextIO): 输出流，默认 sys.stdout。
        """
        self.initialize()

        out.write(f"P3\n{self._image_width} {self.image_height}\n255\n")

        for j in range(self.image_height):
            sys.stderr.write(f"\rScanlines remaining: {self.image_height - j} ")
            sys.stderr.flush()
            for i in range(self._image_width):
                pixel_center = (
                        self.pixel00_loc
                        + (i * self.pixel_delta_u)
                        + (j * self.pixel_delta_v)
                )
                ray_direction = pixel_center - self.center
                ray = Ray(self.center, ray_direction)

                pixel_color = self.ray_color(ray, world)
                write_color(out, pixel_color)

        sys.stderr.write("\rDone.")
        sys.stderr.flush()

    def initialize(self) -> None:
        """
        根据公共参数计算图像高度与视口/像素网格（对应 C++ camera::initialize）。

        视口高度固定为 2.0，焦距固定为 1.0，相机位于原点、朝 -Z 看。
        结果写入私有状态：image_height、center、pixel00_loc、
        pixel_delta_u、pixel_delta_v。
        """
        # 计算图像高度，并保证至少为 1 像素
        self.image_height = int(self._image_width / self._aspect_ratio)
        self.image_height = 1 if self.image_height < 1 else self.image_height

        # 相机位于原点
        self.center = Point3(0, 0, 0)

        # 视口尺寸。视口高度固定为 2.0，焦距为 1.0。
        focal_length = 1.0
        viewport_height = 2.0
        viewport_width = viewport_height * (self._image_width / self.image_height)

        # 视口水平与垂直方向（向右为 +u，向下为 +v）的边向量
        viewport_u = Vec3(viewport_width, 0, 0)
        viewport_v = Vec3(0, -viewport_height, 0)

        # 像素到像素的增量向量
        self.pixel_delta_u = viewport_u / self._image_width
        self.pixel_delta_v = viewport_v / self.image_height

        # 视口左上角及像素 (0,0) 的中心位置
        viewport_upper_left = (
                self.center
                - Vec3(0, 0, focal_length)
                - viewport_u / 2
                - viewport_v / 2
        )
        self.pixel00_loc = (
                viewport_upper_left + 0.5 * (self.pixel_delta_u + self.pixel_delta_v)
        )

    def ray_color(self, ray: Ray, world: Hittable) -> Color:
        """
        计算单条光线 ray 在场景 world 中的颜色（对应 C++ camera::ray_color）。

        命中物体时，以交点处的单位法线映射到 RGB：0.5 * (N + 1)；
        未命中时，按光线方向的 y 分量插值出天空渐变背景色。

        Args:
            ray (Ray): 待着色的光线，原点为相机位置，方向指向某像素。
            world (Hittable): 待检测的场景。

        Returns:
            Color: 该光线对应的颜色。
        """
        hit_record: HitRecord | None = world.hit(ray, Interval(0.0, math.inf))
        if hit_record is not None:
            # 命中：以交点处单位法线映射着色（0.5 * (N + 1)）
            return (hit_record.normal + Color(1.0, 1.0, 1.0)) / 2

        # 未命中：天空渐变背景
        unit_direction = ray.direction.unit_vector()
        a = (unit_direction.y + 1.0) / 2
        color: Color = (1.0 - a) * Color(1.0, 1.0, 1.0) + a * Color(0.5, 0.7, 1.0)
        return color


if __name__ == "__main__":
    import io

    from HittableList import HittableList
    from Sphere import Sphere

    # 构造并初始化：宽高比 16/9、宽 400 -> 高应为 225
    cam = Camera(aspect_ratio=16 / 9, image_width=400)
    cam.initialize()
    print(f"image_height: {cam.image_height}")
    assert cam.image_height == 225
    assert cam.center == Point3(0, 0, 0)

    # 视口宽度应与宽高比匹配：viewport_height=2.0, width=2.0 * 400/225
    expected_viewport_width = 2.0 * (400 / 225)
    # 由像素增量反推 viewport 宽度
    derived = cam.pixel_delta_u.x * cam._image_width
    print(f"viewport_width derived: {derived}")
    assert abs(derived - expected_viewport_width) < 1e-9

    # 像素 (0,0) 中心位置：左上角向内偏移半格，且 z 应为 -1（焦距 1.0）
    print(f"pixel00_loc: {cam.pixel00_loc}")
    assert abs(cam.pixel00_loc.z - (-1.0)) < 1e-9

    # 渲染极小场景到内存，校验 PPM 头与像素数
    tiny = Camera(aspect_ratio=1.0, image_width=3)
    world = HittableList(Sphere(Point3(0, 0, -1), 0.5))
    buf = io.StringIO()
    tiny.render(world, out=buf)
    lines = buf.getvalue().splitlines()
    print(f"PPM header: {lines[0]} {lines[1]} {lines[2]}")
    assert lines[0] == "P3"
    assert lines[1] == "3 3"
    assert lines[2] == "255"
    # 3x3 图像应有 9 行 RGB
    assert len(lines) == 3 + 9

    print("\n所有测试通过")
