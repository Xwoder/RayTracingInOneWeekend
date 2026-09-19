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
      samples_per_pixel（每像素采样数）、max_depth（光线最大反弹次数）、
      vfov（垂直视角，单位度）、lookfrom（相机位置）、lookat（注视点）、
      vup（相机相对「上」方向）。
    - render(world, out)：按 PPM 格式输出图像。
    - 私有状态：image_height、pixel_samples_scale、center、pixel00_loc、
      pixel_delta_u、pixel_delta_v、u、v、w，由 initialize() 根据公共参数计算。
    - ray_color(r, depth, world)：对单条光线着色（depth 用尽返回黑色；
      命中物体时把散射委托给物体材质 rec.material.scatter，否则返回天空渐变背景）。

    对应 C++ 的：
        class camera {
          public:
            double aspect_ratio      = 1.0;
            int    image_width       = 100;
            int    samples_per_pixel = 10;
            int    max_depth         = 10;
            double vfov              = 90;  // 垂直视角（field of view）
            void render(const hittable& world);
          private:
            void initialize();
            color ray_color(const ray& r, int depth, const hittable& world) const;
        };
    """
    _aspect_ratio: Number = 1
    _image_width: int = 0
    _image_height: int = 0
    _samples_per_pixel: int = 10
    _max_depth: int = 10
    _vfov: Number = 90
    _lookfrom: Point3 = Point3(0, 0, 0)
    _lookat: Point3 = Point3(0, 0, -1)
    _vup: Vec3 = Vec3(0, 1, 0)

    _pixel_samples_scale: Number = 1
    _center: Point3 = Point3(0, 0, 0)
    _pixel00_loc: Point3 = Point3(0, 0, 0)
    _pixel_delta_u: Vec3 = Vec3(0, 0, 0)
    _pixel_delta_v: Vec3 = Vec3(0, 0, 0)
    _u: Vec3 = Vec3(0, 0, 0)
    _v: Vec3 = Vec3(0, 0, 0)
    _w: Vec3 = Vec3(0, 0, 0)

    def __init__(self,
                 aspect_ratio: Number = 1,
                 image_width: int = 400,
                 samples_per_pixel: int = 10,
                 max_depth: int = 10,
                 vfov: Number = 90,
                 lookfrom: Point3 | None = None,
                 lookat: Point3 | None = None,
                 vup: Vec3 | None = None):
        """
        构造一台相机。

        Args:
            aspect_ratio (float): 图像宽高比（宽度 / 高度），默认 1.0。
            image_width (int): 渲染图像的像素宽度，默认 100。
            samples_per_pixel (int): 每个像素的采样次数，默认 10。
            max_depth (int): 光线进入场景后最大的反弹（bounce）次数，默认 10。
            vfov (float): 垂直视角（field of view），单位度，默认 90。
            lookfrom (Point3): 相机所在位置（看向哪里），默认 (0,0,0)。
            lookat (Point3): 相机注视的目标点，默认 (0,0,-1)。
            vup (Vec3): 相机相对的「上」方向，默认 (0,1,0)。
        """
        self._aspect_ratio = aspect_ratio
        self._image_width = image_width
        self._samples_per_pixel = samples_per_pixel
        self._max_depth = max_depth
        self._vfov = vfov
        self._lookfrom = lookfrom if lookfrom is not None else Point3(0, 0, 0)
        self._lookat = lookat if lookat is not None else Point3(0, 0, -1)
        self._vup = vup if vup is not None else Vec3(0, 1, 0)

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

        out.write(f"P3\n{self._image_width} {self._image_height}\n255\n")

        for j in range(self._image_height):
            sys.stderr.write(f"\rScanlines remaining: {self._image_height - j} ")
            sys.stderr.flush()
            for i in range(self._image_width):
                pixel_color = Color(0, 0, 0)
                for _ in range(self._samples_per_pixel):
                    ray: Ray = self.get_ray(i, j)
                    color: Color = self.ray_color(ray, self._max_depth, world)
                    pixel_color += color

                pixel_color *= self._pixel_samples_scale

                write_color(out, pixel_color)

        sys.stderr.write("\rDone.")
        sys.stderr.flush()

    def initialize(self) -> None:
        """
        根据公共参数计算图像高度、相机坐标系与视口/像素网格
        （对应 C++ camera::initialize）。

        焦距由观景点距离决定：focal_length = |lookfrom - lookat|。
        以 lookfrom/lookat/vup 为基准求出相机坐标架 u、v、w，
        再据此摆放视口与像素网格。结果写入私有状态：image_height、
        pixel_samples_scale、center、pixel00_loc、pixel_delta_u、
        pixel_delta_v、u、v、w。
        """
        # 计算图像高度，并保证至少为 1 像素
        self._image_height = int(self._image_width / self._aspect_ratio)
        self._image_height = 1 if self._image_height < 1 else self._image_height

        self._pixel_samples_scale = 1.0 / self._samples_per_pixel

        self._center = self._lookfrom

        # 视口尺寸。焦距取相机到注视点的距离，视口高度由垂直视角 vfov 决定：
        #   focal_length = |lookfrom - lookat|
        #   theta = radians(vfov), h = tan(theta/2)
        #   viewport_height = 2 * h * focal_length
        # vfov=90 且相机位于原点朝 -Z 看时，退化为原来的固定高度 2.0。
        focal_length = (self._lookfrom - self._lookat).length()
        theta = math.radians(self._vfov)
        h = math.tan(theta / 2)
        viewport_height = 2 * h * focal_length
        viewport_width = viewport_height * (self._image_width / self._image_height)

        # 计算相机坐标架的三个单位基向量 u、v、w。
        self._w = (self._lookfrom - self._lookat).unit_vector()
        self._u = Vec3.cross(self._vup, self._w).unit_vector()
        self._v = Vec3.cross(self._w, self._u)

        # 沿视口水平（向右）与垂直（向下）方向的边向量。
        viewport_u = viewport_width * self._u
        viewport_v = viewport_height * -self._v

        # 像素到像素的增量向量
        self._pixel_delta_u = viewport_u / self._image_width
        self._pixel_delta_v = viewport_v / self._image_height

        # 视口左上角及像素 (0,0) 的中心位置
        viewport_upper_left = (
                self._center
                - focal_length * self._w
                - viewport_u / 2
                - viewport_v / 2
        )
        self._pixel00_loc = (
                viewport_upper_left + 0.5 * (self._pixel_delta_u + self._pixel_delta_v)
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
                self._pixel00_loc
                + ((i + offset.x) * self._pixel_delta_u)
                + ((j + offset.y) * self._pixel_delta_v)
        )

        ray_origin = self._center
        ray_direction = pixel_sample - ray_origin

        ray: Ray = Ray(ray_origin, ray_direction)
        return ray

    def ray_color(self, ray: Ray, depth: int, world: Hittable) -> Color:
        """
        计算单条光线 ray 在场景 world 中的颜色（对应 C++ camera::ray_color）。

        先检查反弹深度 depth：若已用尽（depth <= 0），不再收集任何光，返回黑色。
        命中物体时，将散射委托给该物体材质 rec.material.scatter(...)：
        若发生散射，则返回 衰减系数 * 递归着色(散射光线, depth-1)；
        若材质吸收光线（无散射），返回黑色。
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
        if hit_record is not None and hit_record.material is not None:
            # 命中：把散射完全交给材质（Lambertian / 金属 / ...）处理。
            # scatter 命中时返回 (衰减系数, 散射光线)，被吸收时返回 None。
            result = hit_record.material.scatter(ray, hit_record)
            if result is not None:
                attenuation, scattered = result
                return attenuation * self.ray_color(scattered, depth - 1, world)
            return Color(0, 0, 0)

        # 未命中：天空渐变背景
        unit_direction = ray.direction.unit_vector()
        a = (unit_direction.y + 1.0) / 2
        color: Color = (1.0 - a) * Color(1.0, 1.0, 1.0) + a * Color(0.5, 0.7, 1.0)
        return color

    @property
    def image_width(self):
        return self._image_width

    @property
    def image_height(self):
        return self._image_height

    @property
    def vfov(self):
        return self._vfov

    @property
    def lookfrom(self):
        return self._lookfrom

    @property
    def lookat(self):
        return self._lookat

    @property
    def vup(self):
        return self._vup
