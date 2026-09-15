from abc import ABC, abstractmethod

from HitRecord import HitRecord
from Ray import Ray


class Hitable(ABC):
    """
    可命中物体接口（抽象基类）

    任何能够被光线检测（求交）的物体都应实现该接口，提供 hit 方法。
    对应《Ray Tracing in One Weekend》中的 hittable 抽象。
    """

    @abstractmethod
    def hit(self, r: Ray) -> HitRecord | None:
        """
        判断光线 r 是否击中本物体。

        Args:
            r (Ray): 待检测的光线。

        Returns:
            HitRecord | None: 命中时返回记录交点信息的 HitRecord；未命中返回 None。
        """
        ...
