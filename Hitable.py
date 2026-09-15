import math

from abc import ABC, abstractmethod

from HitRecord import HitRecord
from Number import Number
from Ray import Ray


class Hitable(ABC):
    """
    可命中物体接口（抽象基类）

    任何能够被光线检测（求交）的物体都应实现该接口，提供 hit 方法。
    对应《Ray Tracing in One Weekend》中的 hittable 抽象。
    """

    @abstractmethod
    def hit(
        self,
        ray: Ray,
        ray_t_min: Number = 0.0,
        ray_t_max: Number = math.inf,
    ) -> HitRecord | None:
        """
        判断光线 ray 是否击中本物体，并可限制命中参数 t 的搜索区间。

        Args:
            ray (Ray): 待检测的光线。
            ray_t_min (Number): 光线参数 t 的下界（不含），默认 0.0。
            ray_t_max (Number): 光线参数 t 的上界（不含），默认为正无穷。

        Returns:
            HitRecord | None: 命中时返回记录交点信息的 HitRecord；未命中返回 None。
        """
        ...
