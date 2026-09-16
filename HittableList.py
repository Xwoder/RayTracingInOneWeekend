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


if __name__ == "__main__":
    from Point3 import Point3
    from Sphere import Sphere
    from Vec3 import Vec3

    # 两个共线的球：近球在 z=-1 半径 0.5，远球在 z=-3 半径 0.5
    near = Sphere(Point3(0, 0, -1), 0.5)
    far = Sphere(Point3(0, 0, -3), 0.5)

    world = HittableList()
    assert len(world) == 0
    world.add(near)
    world.add(far)
    # __len__ 返回物体数量
    assert len(world) == 2

    # 用构造函数直接加入
    world2 = HittableList(near)
    assert len(world2) == 1

    # 沿 -z 方向、从原点射出应命中近球（t≈0.5），而非远球（t≈2.5）
    r = Ray(Point3(0, 0, 0), Vec3(0, 0, -1))
    rec = world.hit(r)
    print(f"hit (命中近球): {rec}")
    assert rec is not None
    assert abs(rec.t - 0.5) < 1e-9
    assert rec.point == Point3(0, 0, -0.5)
    assert rec.front_face is True  # 光线从球外射入，命中正面

    # 下界限制为 [2.0, +∞) 时，近球（t≈0.5 与远交点 t≈1.5）均被排除，
    # 应命中远球（t≈2.5）
    rec_far = world.hit(r, Interval(2.0, math.inf))
    print(f"hit (限制下界命中远球): {rec_far}")
    assert rec_far is not None
    assert abs(rec_far.t - 2.5) < 1e-9

    # 完全错过（沿 +x 偏离）：列表也应返回 None
    r_miss = Ray(Point3(5, 0, 0), Vec3(0, 0, -1))
    assert world.hit(r_miss) is None

    # clear 清空后不再命中
    world.clear()
    assert len(world) == 0
    assert world.hit(r) is None

    print("\n所有测试通过")
