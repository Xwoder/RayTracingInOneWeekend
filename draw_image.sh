#!/bin/bash

unset VIRTUAL_ENV

uv run python main.py > image.PPM

open image.PPM
