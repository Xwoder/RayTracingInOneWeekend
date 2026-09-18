#!/bin/bash

unset VIRTUAL_ENV

OUTPUT_DIR="output"
mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +"%Y_%m_%d_%H_%M_%S")
OUTPUT="${OUTPUT_DIR}/image_${TIMESTAMP}.PPM"

uv run python main.py > "$OUTPUT"

open "$OUTPUT"
