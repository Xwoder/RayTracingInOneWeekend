"""Color 模块的 pytest 测试（由 Color.py 原 __main__ 自测块迁移而来）。

运行：
    .venv/bin/python -m pytest tests/test_color.py -v
"""

import io

import pytest

from Color import Color, linear_to_gamma, write_color


# ---------------------------------------------------------------------------
# linear_to_gamma：gamma 2 校正
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "linear, expected",
    [
        (0.25, 0.5),  # sqrt(0.25) = 0.5
        (0.0, 0.0),
        (-1.0, 0.0),  # 非正输入直接返回 0.0（不取负根）
    ],
)
def test_linear_to_gamma(linear: float, expected: float):
    assert linear_to_gamma(linear) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# write_color：伽马校正 + 钳制到 [0,255] + 写入 "R G B\n"
# ---------------------------------------------------------------------------
def test_write_color_normalized():
    # (1.0, 0.5, 0.25) -> gamma -> (1.0, sqrt(0.5), sqrt(0.25))
    # = (1.0, 0.7071.., 0.5) -> 字节 (255, 180, 127)
    buf = io.StringIO()
    write_color(buf, Color(1.0, 0.5, 0.25))
    assert buf.getvalue() == "255 180 127\n"


def test_write_color_clamps_overflow():
    # write_color 先 gamma 再 intensity.clamp 到 [0,1]；
    # r=5.0 -> gamma(5.0)=sqrt(5)=2.236 -> 钳到 1.0 -> 255（不报错、不溢出）
    buf = io.StringIO()
    write_color(buf, Color(5.0, 0.5, 0.25))
    assert buf.getvalue() == "255 180 127\n"
