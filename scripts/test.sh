#!/usr/bin/env bash

set -e
set -x

bash ./scripts/test-files.sh
poetry run pytest --cov=drifactorial --cov=tests --cov=docs_src --cov-report=term-missing --cov-report=html --cov-report=xml -o console_output_style=progress "${@}"
