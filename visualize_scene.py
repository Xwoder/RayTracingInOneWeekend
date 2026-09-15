"""
visualize_scene.py

用 Matplotlib 3D 可视化 Ray Tracing in One Weekend 中的场景关系：
    - 相机 (Camera)
    - 取景窗 / 视口 (Viewport)
    - 球 (Sphere)
    - 从相机发出、穿过视口像素的光线 (Rays)

本脚本直接复用项目里已有的类：Camera / Sphere / Ray / Vec3 / Point3，
所有场景参数都与 main.py 保持一致，运行后会弹出 Matplotlib 的交互窗口，
可以用鼠标拖动旋转、缩放，从任意角度观察各物体的相对关系。
"""

from __future__ import annotations

try:
    import matplotlib

    matplotlib.use("TkAgg")  # 弹出独立窗口；macOS/Linux/Windows 通用
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (确保 3D 支持)
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
except ImportError:
    raise SystemExit(
        "缺少 matplotlib。请先在虚拟环境中安装：\n"
        "    pip install matplotlib\n"
        "或：\n"
        "    uv pip install matplotlib"
    )

import matplotlib.font_manager as fm
import numpy as np

# 优先使用系统中文字体，避免标题/标注在弹窗里显示为方框
_CJK_FONTS = [
    "Arial Unicode MS", "PingFang SC", "Hiragino Sans GB",
    "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC",
]
_available_fonts = {f.name for f in fm.fontManager.ttflist}
_chosen = next((f for f in _CJK_FONTS if f in _available_fonts), None)
if _chosen:
    plt.rcParams["font.family"] = _chosen
else:
    print("提示：未找到支持中文的字体，文字标注可能显示为方框。")

from Camera import Camera
from Ray import Ray
from Sphere import Sphere
from Vec3 import Point3, Vec3


# ----------------------------------------------------------------------
# 1. 与 main.py 完全一致的场景参数
# ----------------------------------------------------------------------
ASPECT_RATIO = 16 / 9
IMAGE_WIDTH = 800
IMAGE_HEIGHT = int(IMAGE_WIDTH / ASPECT_RATIO)

camera = Camera()  # 位置 (0, 0, 0)，朝向 +Z（视线方向由 focal_direction 决定）

FOCAL_LENGTH = 1.0
focal_direction = Vec3(0, 0, FOCAL_LENGTH)

viewport_height = 2.0
viewport_width = viewport_height * (IMAGE_WIDTH / IMAGE_HEIGHT)

viewport_u = Vec3(viewport_width, 0, 0)      # 视口水平边（沿 +x，宽）
viewport_v = Vec3(0, -viewport_height, 0)    # 视口垂直边（沿 -y，高）

pixel_delta_u = viewport_u / IMAGE_WIDTH
pixel_delta_v = viewport_v / IMAGE_HEIGHT

viewport_center = camera.position - focal_direction
viewport_upper_left = viewport_center - viewport_u / 2 - viewport_v / 2
pixel00_loc = viewport_upper_left + (pixel_delta_u + pixel_delta_v) / 2

# 场景中待检测的物体（与 main.py 一致）
sphere = Sphere(Point3(0, 0, -1), 0.5)


def pixel_center(col: int, row: int) -> Point3:
    """返回第 (row, col) 个像素中心的 world 坐标。"""
    return pixel00_loc + (col * pixel_delta_u) + (row * pixel_delta_v)


# ----------------------------------------------------------------------
# 2. 准备几何数据
# ----------------------------------------------------------------------
# 视口（viewport）的四个角
vp_UL = viewport_upper_left
vp_UR = vp_UL + viewport_u
vp_LL = vp_UL + viewport_v
vp_LR = vp_UL + viewport_u + viewport_v

# 球体表面（用于画线框）
theta = np.linspace(0, np.pi, 24)
phi = np.linspace(0, 2 * np.pi, 36)
TH, PH = np.meshgrid(theta, phi)
sx = sphere.center.x + sphere.radius * np.sin(TH) * np.cos(PH)
sy = sphere.center.y + sphere.radius * np.sin(TH) * np.sin(PH)
sz = sphere.center.z + sphere.radius * np.cos(TH)

# 选取 3x3 个采样像素，发出示例光线
sample_fracs = [0.15, 0.5, 0.85]
sample_cols = [int(f * IMAGE_WIDTH) for f in sample_fracs]
sample_rows = [int(f * IMAGE_HEIGHT) for f in sample_fracs]

rays_info = []  # (origin, endpoint, is_hit)
for r in sample_rows:
    for c in sample_cols:
        pc = pixel_center(c, r)
        ray = Ray(camera.position, pc - camera.position)
        t = sphere.hit(ray)
        if t is not None and t > 0:
            end = ray.at(t)            # 命中：停在球面
            is_hit = True
        else:
            # 未命中：沿原方向延长到 z = -3 处
            target_z = -3.0
            tt = (target_z - camera.position.z) / ray.direction.z
            end = ray.at(tt)
            is_hit = False
        rays_info.append((camera.position, end, is_hit))


# ----------------------------------------------------------------------
# 3. 绘图
# ----------------------------------------------------------------------
fig = plt.figure(figsize=(11, 8))
ax = fig.add_subplot(111, projection="3d")

# --- 坐标轴 ---
ax.set_xlabel("X (右)")
ax.set_ylabel("Y (上)")
ax.set_zlabel("Z (朝向观察者)")
ax.set_title("Ray Tracing 场景关系：相机 / 视口 / 球 / 光线")

# --- 视口（半透明矩形平面 + 边框）---
viewport_poly = Poly3DCollection(
    [[(vp_UL.x, vp_UL.y, vp_UL.z),
      (vp_UR.x, vp_UR.y, vp_UR.z),
      (vp_LR.x, vp_LR.y, vp_LR.z),
      (vp_LL.x, vp_LL.y, vp_LL.z)]],
    alpha=0.18, facecolor="cyan", edgecolor="teal", linewidths=2,
)
ax.add_collection3d(viewport_poly)

# --- 球（线框） ---
ax.plot_wireframe(sx, sy, sz, rstride=2, cstride=2, color="red", alpha=0.85, linewidth=0.6)

# --- 相机（原点处的标记 + 视线方向箭头） ---
ax.scatter(
    [camera.position.x], [camera.position.y], [camera.position.z],
    color="black", s=120, marker="o", depthshade=False, label="相机 Camera",
)
view_axis = vp_UL - camera.position  # 中心视线方向（指向视口）
ax.quiver(
    camera.position.x, camera.position.y, camera.position.z,
    view_axis.x, view_axis.y, view_axis.z,
    color="black", arrow_length_ratio=0.12, linewidth=2,
)

# --- 示例光线 ---
for origin, end, is_hit in rays_info:
    color = "orange" if is_hit else "gray"
    ls = "-" if is_hit else "--"
    lw = 2.2 if is_hit else 1.0
    ax.plot(
        [origin.x, end.x], [origin.y, end.y], [origin.z, end.z],
        color=color, linestyle=ls, linewidth=lw,
    )
    if is_hit:
        ax.scatter([end.x], [end.y], [end.z], color="orange", s=40, depthshade=False)

# --- 标注文字 ---
ax.text(camera.position.x, camera.position.y, camera.position.z + 0.15,
        "Camera", color="black", fontsize=10, weight="bold")
ax.text(viewport_center.x, viewport_center.y + viewport_height / 2 + 0.15, viewport_center.z,
        "Viewport", color="teal", fontsize=10, weight="bold")
ax.text(sphere.center.x, sphere.center.y, sphere.center.z + sphere.radius + 0.15,
        "Sphere", color="red", fontsize=10, weight="bold")

# --- 图例（光线说明） ---
from matplotlib.lines import Line2D
legend_handles = [
    Line2D([0], [0], color="orange", lw=2.2, label="命中球面的光线"),
    Line2D([0], [0], color="gray", lw=1.5, linestyle="--", label="未命中(掠过)的光线"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="black",
           markersize=8, label="相机 Camera"),
]
ax.legend(handles=legend_handles, loc="upper left")

# --- 统一坐标轴比例，避免物体被拉伸 ---
all_pts = np.array([
    [camera.position.x, camera.position.y, camera.position.z],
    [vp_UL.x, vp_UL.y, vp_UL.z], [vp_UR.x, vp_UR.y, vp_UR.z],
    [vp_LL.x, vp_LL.y, vp_LL.z], [vp_LR.x, vp_LR.y, vp_LR.z],
    [sphere.center.x - sphere.radius, sphere.center.y - sphere.radius, sphere.center.z - sphere.radius],
    [sphere.center.x + sphere.radius, sphere.center.y + sphere.radius, sphere.center.z + sphere.radius],
])
centers = all_pts.mean(axis=0)
ranges = (all_pts.max(axis=0) - all_pts.min(axis=0)) / 2
span = float(ranges.max()) * 1.3
ax.set_xlim(centers[0] - span, centers[0] + span)
ax.set_ylim(centers[1] - span, centers[1] + span)
ax.set_zlim(centers[2] - span, centers[2] + span)
try:
    ax.set_box_aspect((1, 1, 1))
except Exception:
    pass

plt.tight_layout()
plt.show()
