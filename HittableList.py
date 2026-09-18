import math
from typing import override

from HitRecord import HitRecord
from Hittable import Hittable
from Interval import Interval
from Number import Number
from Ray import Ray


class HittableList(Hittable):
    """
    可命中物体列表（场景容器）

    持有多个可命中物体（Hittable），并把 hit 检测委托给其中的每一个，
    返回所有物体中最靠近光线原点（t 最小）的那次命中记录。

    对应《Ray Tracing in One Weekend》中的 hittable_list：
        - objects 容器（C++ 的 std::vector<shared_ptr<hittable>>）
        - add()  往容器中追加一个物体
        - clear() 清空容器
        - hit()  遍历所有物体，保留 ray_t 区间内 t 最小的那条命中
    """

    _objects: list[Hittable]

    def __init__(self, obj: Hittable | None = None):
        """
        构造一个可命中物体列表，可选地直接加入一个初始物体。

        Args:
            obj (Hittable | None): 可选的初始物体；提供时等价于构造后再 add 一次。
        """
        self._objects: list[Hittable] = []
        if obj is not None:
            self.add(obj)

    def clear(self) -> None:
        """清空列表中的所有物体（对应 C++ 的 clear()）。"""
        self._objects.clear()

    def __len__(self) -> int:
        """
        返回列表中可命中物体的数量（对应 C++ objects.size()）。

        实现后可直接用内置 len() 获取元素个数，例如 len(world)。

        Returns:
            int: 当前列表中的物体数量。
        """
        return len(self._objects)

    def add(self, obj: Hittable) -> None:
        """
        向列表中追加一个可命中物体（对应 C++ 的 add()）。

        Args:
            obj (Hittable): 要加入场景的物体，必须实现 Hittable 接口。
        """
        self._objects.append(obj)

    @override
    def hit(
            self,
            ray: Ray,
            ray_t: Interval = Interval(0.0, math.inf),
    ) -> HitRecord | None:
        """
        检测光线是否击中列表中的任意物体，并返回最近的一次命中。

        遍历所有物体，仅保留落在区间 ray_t 内、且 t 比当前
        已知最近命中更小的那次命中（closest_so_far 随命中不断收紧上界），
        从而保证最终得到的是最近交点。

        对应 C++ hittable_list::hit 的逻辑：命中时更新 closest_so_far 与 rec，
        最后返回是否击中任何物体。

        Args:
            ray (Ray): 待检测的光线。
            ray_t (Interval): 光线参数 t 的有效区间（开区间，不含端点），
                默认 Interval(0.0, +inf) 即 [0, +∞)。

        Returns:
            HitRecord | None: 命中最近物体时返回其 HitRecord；若全未命中返回 None。
        """
        closest_so_far: Number = ray_t.max
        hit_record: HitRecord | None = None

        for obj in self._objects:
            temp_hit_record: HitRecord | None = obj.hit(
                ray, Interval(ray_t.min, closest_so_far)
            )
            if temp_hit_record is not None:
                closest_so_far = temp_hit_record.t
                hit_record = temp_hit_record

        return hit_record


