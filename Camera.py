import math
import sys
from typing import TextIO

from Color import Color, write_color
from HitRecord import HitRecord
from Hittable import Hittable
from Interval import Interval
from Number import Number
from Point3 import Point3
from Random import random_number
from Ray import Ray
from Vec3 import Vec3


class Camera:
    """
    相机类（参考《Ray Tracing in One Weekend》的 camera 实现）

    封装渲染一帧所需的所有参数与逻辑：

    - 公共参数：aspect_ratio（宽高比）、image_width（像素宽度）、
      samples_per_pixel（每像素采样数）、max_depth（光线最大反弹次数）。
    - render(world, out)：按 PPM 格式输出图像。
    - 私有状态：image_height、center、pixel00_loc、pixel_delta_u、
      pixel_delta_v，由 initialize() 根据公共参数计算。
    - ray_color(r, depth, world)：对单条光线着色（depth 用尽返回黑色；
      命中物体后沿法线所在半球内的随机方向继续漫反射，否则返回天空渐变背景）。

    对应 C++ 的：
        class camera {
          public:
            double aspect_ratio      = 1.0;
            int    image_width       = 100;
            int    samples_per_pixel = 10;
            int    max_depth         = 10;
            void render(const hittable& world);
          private:
            void initialize();
            color ray_color(const ray& r, int depth, const hittable& world) const;
        };
    """
    _aspect_ratio: Number
    _image_width: int
    _samples_per_pixel: int = 10
    _max_depth: int = 10

    def __init__(self,
                 aspect_ratio: Number = 1,
                 image_width: int = 400,
                 samples_per_pixel: int = 10,
                 max_depth: int = 10):
        """
        构造一台相机。

        Args:
            aspect_ratio (float): 图像宽高比（宽度 / 高度），默认 1.0。
            image_width (int): 渲染图像的像素宽度，默认 100。
            samples_per_pixel (int): 每个像素的采样次数，默认 10。
            max_depth (int): 光线进入场景后最大的反弹（bounce）次数，默认 10。
        """
        self._aspect_ratio = aspect_ratio
        self._image_width = image_width
        self._samples_per_pixel = samples_per_pixel
        self._max_depth = max_depth

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
                pixel_color = Color(0, 0, 0)
                for _ in range(self._samples_per_pixel):
                    ray: Ray = self.get_ray(i, j)
                    color: Color = self.ray_color(ray, self._max_depth, world)
                    pixel_color += color

                pixel_color /= self._samples_per_pixel

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

    def sample_square(self) -> Vec3:
        """
        返回 [-.5,-.5]-[+.5,+.5] 单位方形内的随机点。

        在一个像素内部随机选取一个位置，并返回这个位置相对于像素中心的二维偏移量。
        用于抗锯齿：在每个像素内随机抖动采样点，使边缘锯齿被平均掉。

        Returns:
            Vec3: z 分量为 0 的随机偏移向量。
        """
        return Vec3(x=random_number() - 0.5,
                    y=random_number() - 0.5,
                    z=0)

    def get_ray(self, i: int, j: int) -> Ray:
        """
        构造一条从相机原点射向像素 (i, j) 附近随机采样点的光线。

        像素 (i, j) 的真实中心会因 sample_square() 的随机偏移而抖动，
        因此每个像素会发射多条略有差异的光线，最终由 render 求平均实现抗锯齿。

        Args:
            i (int): 像素列下标（水平方向，对应 pixel_delta_u）。
            j (int): 像素行下标（垂直方向，对应 pixel_delta_v）。

        Returns:
            Ray: 经过随机抖动的相机光线。
        """
        offset: Vec3 = self.sample_square()
        pixel_sample: Point3 = (
                self.pixel00_loc
                + ((i + offset.x) * self.pixel_delta_u)
                + ((j + offset.y) * self.pixel_delta_v)
        )

        ray_origin = self.center
        ray_direction = pixel_sample - ray_origin

        ray: Ray = Ray(ray_origin, ray_direction)
        return ray

    def ray_color(self, ray: Ray, depth: int, world: Hittable) -> Color:
        """
        计算单条光线 ray 在场景 world 中的颜色（对应 C++ camera::ray_color）。

        先检查反弹深度 depth：若已用尽（depth <= 0），不再收集任何光，返回黑色。
        命中物体时，沿交点处法线所在半球内的随机方向生成一条新光线并
        递归着色（漫反射 / Lambertian，depth 减 1），结果乘以 0.5；
        未命中时，按光线方向的 y 分量插值出天空渐变背景色。

        Args:
            ray (Ray): 待着色的光线，原点为相机位置，方向指向某像素。
            depth (int): 剩余可用的反弹次数；每反弹一次递减，归零即停止。
            world (Hittable): 待检测的场景。

        Returns:
            Color: 该光线对应的颜色。
        """
        # 反弹次数用尽，不再收集光，返回黑色
        if depth <= 0:
            return Color(0, 0, 0)

        hit_record: HitRecord | None = world.hit(ray, Interval(0.001, math.inf))
        if hit_record is not None:
            # 命中：Lambertian 漫反射
            # 在表面法线方向上叠加一个随机单位向量，得到法线所在半球内
            # 的随机散射方向（即余弦加权采样，等价于在半球内均匀取方向）
            direction: Vec3 = hit_record.normal + Vec3.random_unit_vector()
            return 0.7 * self.ray_color(Ray(hit_record.point, direction), depth - 1, world)

        # 未命中：天空渐变背景
        unit_direction = ray.direction.unit_vector()
        a = (unit_direction.y + 1.0) / 2
        color: Color = (1.0 - a) * Color(1.0, 1.0, 1.0) + a * Color(0.5, 0.7, 1.0)
        return color


if __name__ == "__main__":
    import io

    from HittableList import HittableList
    from Lambertian import Lambertian
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
    world = HittableList(Sphere(Point3(0, 0, -1), 0.5, Lambertian(Color(0.5, 0.5, 0.5))))
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
