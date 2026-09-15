from dataclasses import dataclass

from Number import Number
from Vec3 import Point3, Vec3


@dataclass
class HitRecord:
    """
    命中记录

    记录一条光线击中某物体时的关键信息：
        - p      交点坐标（对应 C++ 的 point3 p）
        - normal 交点处的单位法向量（对应 C++ 的 vec3 normal）
        - t      光线参数方程 P(t) = origin + t * direction 中的参数值
    由 Hitable.hit() 填充后，着色阶段即可读取这些数据进行渲染。
    """

    p: Point3
    normal: Vec3
    t: Number
