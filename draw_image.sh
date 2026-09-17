#!/bin/bash

unset VIRTUAL_ENV

TIMESTAMP=$(date +"%Y_%m_%d_%H_%M_%S")
OUTPUT="image_${TIMESTAMP}.PPM"

uv run python main.py > "$OUTPUT"

open "$OUTPUT"
