from abc import ABC, abstractmethod

from Color import Color
from HitRecord import HitRecord
from Ray import Ray


class Material(ABC):
    """
    材质抽象基类

    决定一条光线击中物体表面后如何散射（或被吸收），是着色逻辑的核心。
    对应《Ray Tracing in One Weekend》中的 material 抽象类：

        class material {
          public:
            virtual ~material() = default;
            virtual bool scatter(
                const ray& r_in, const hit_record& rec,
                color& attenuation, ray& scattered
            ) const { return false; }
        };

    C++ 版本通过返回 bool 并写入 attenuation / scattered 两个「出参引用」来传达结果；
    在 Python 中我们直接返回 (attenuation, scattered) 元组，未散射时返回 None，语义等价。
    """

    @abstractmethod
    def scatter(self, r_in: Ray, rec: HitRecord) -> tuple[Color, Ray] | None:
        """
        计算入射光线 r_in 在 rec 处命中后的散射结果。

        子类必须实现本方法。

        Args:
            r_in (Ray): 入射光线。
            rec (HitRecord): 命中记录（交点、法线、t、front_face 等）。

        Returns:
            tuple[Color, Ray] | None:
                若发生散射，返回 (衰减系数 attenuation, 散射光线 scattered)；
                若光线被吸收（无散射），返回 None。
        """
        ...

