from abc import ABC

from Vec3 import Point3, Vec3


class HitRecord(ABC):
    """
    命中记录（抽象类）

    记录一条光线击中某物体时的关键信息：
        - p      交点坐标（对应 C++ 的 point3 p）
        - normal 交点处的单位法向量（对应 C++ 的 vec3 normal）
        - t      光线参数方程 P(t) = origin + t * direction 中的参数值
    通过 hit() 填充后，着色阶段即可读取这些数据进行渲染。
    """

    _p: Point3
    _normal: Vec3
    _t: float

    def __init__(self, p: Point3, normal: Vec3, t: float):
        """
        构造一条命中记录。

        Args:
            p (Point3): 光线与物体的交点坐标。
            normal (Vec3): 交点处的（单位）法向量。
            t (float): 交点对应的光线参数值。
        """
        self._p = p
        self._normal = normal
        self._t = t

    @property
    def p(self) -> Point3:
        """返回交点坐标（对应 C++ const point3& p）。"""
        return self._p

    @property
    def normal(self) -> Vec3:
        """返回交点处的单位法向量（对应 C++ const vec3& normal）。"""
        return self._normal

    @property
    def t(self) -> float:
        """返回交点对应的光线参数值（对应 C++ double t）。"""
        return self._t
