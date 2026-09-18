import math
from abc import ABC, abstractmethod

from HitRecord import HitRecord
from Interval import Interval
from Ray import Ray


class Hittable(ABC):
    """
    可命中物体接口（抽象基类）

    任何能够被光线检测（求交）的物体都应实现该接口，提供 hit 方法。
    对应《Ray Tracing in One Weekend》中的 hittable 抽象。
    """

    @abstractmethod
    def hit(
            self,
            ray: Ray,
            ray_t: Interval = Interval(0.0, math.inf),
    ) -> HitRecord | None:
        """
        判断光线 ray 是否击中本物体，并可限制命中参数 t 的搜索区间。

        Args:
            ray (Ray): 待检测的光线。
            ray_t (Interval): 光线参数 t 的有效区间（开区间，不含端点），
                默认 Interval(0.0, +inf) 即 [0, +∞)。

        Returns:
            HitRecord | None: 命中时返回记录交点信息的 HitRecord；未命中返回 None。
        """
        ...
