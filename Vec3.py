import math


class Vec3:
    x: float | int
    y: float | int
    z: float | int

    def __init__(self,
                 x: float | int,
                 y: float | int,
                 z: float | int):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def from_scalar(cls, value: tuple[float | int, float | int, float | int]):
        x = value[0]
        y = value[1]
        z = value[2]
        return cls(x, y, z)

    def length(self):
        return math.sqrt(
            self.x ** 2 +
            self.y ** 2 +
            self.z ** 2
        )


if __name__ == '__main__':
    v = Vec3(1, 2, 3)
    s = Vec3.from_scalar(0.5)

    print(v.x, v.y, v.z)
    print(s.x, s.y, s.z)
    print(v.length())
