from dataclasses import dataclass

from Number import Number
from Point3 import Point3
from Ray import Ray
from Vec3 import  Vec3


@dataclass
class HitRecord:
    """
    命中记录

    记录一条光线击中某物体时的关键信息：
        - p          交点坐标（对应 C++ 的 point3 p）
        - normal     交点处的单位法向量，永远与光线方向相对
                     （对应 C++ 的 vec3 normal）
        - t          光线参数方程 P(t) = origin + t * direction 中的参数值
        - front_face 是否命中外表面：True 表示光线从物体外部射入，
                     normal 与 outward_normal 同向；False 表示从内部射出，
                     normal 被翻转到指向光线来的一侧
                     （对应 C++ 的 bool front_face）

    法线应由 set_face_normal() 统一写入，而不是由调用方直接给 normal 赋值，
    从而保证任意位置都有 dot(ray.direction, normal) <= 0。
    """

    point: Point3
    normal: Vec3
    t: Number
    front_face: bool = False

    def set_face_normal(self, ray: Ray, outward_normal: Vec3) -> None:
        """
        根据本命中的入射方向确定法线朝向，并同时设置 front_face 与 normal。

        约定：法线永远指向「迎着光线」的一侧，即 dot(ray.direction, normal) < 0。
        这样无论光线从物体外部射入还是从内部射出，后续着色代码都无需区分。

        Args:
            ray (Ray): 产生本次命中的光线。
            outward_normal (Vec3): 交点处的单位外法线（由球心指向交点）。
                本方法假定其已为单位长度。

        Returns:
            None: 直接修改自身的 front_face 与 normal 字段。
        """
        self.front_face = ray.direction.dot(outward_normal) < 0
        self.normal = outward_normal if self.front_face else -outward_normal
