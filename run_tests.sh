#!/usr/bin/env bash
# 用项目虚拟环境 (.venv) 运行 pytest，避免系统 Python 缺少 numpy 等问题。
# 用法：
#   ./run_tests.sh              # 跑全部测试
#   ./run_tests.sh -v           # 传任意参数给 pytest，例如 -v / -k hit / tests/test_sphere.py
set -euo pipefail

# 切到脚本所在目录（项目根），保证能找到 conftest.py 与 .venv
cd "$(dirname "$0")"

VENV_PYTHON=".venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
    echo "未找到 $VENV_PYTHON，请先创建虚拟环境并安装依赖（uv sync 或 pip install -e .）。" >&2
    exit 1
fi

exec "$VENV_PYTHON" -m pytest "$@"
