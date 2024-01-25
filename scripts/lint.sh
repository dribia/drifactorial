#!/usr/bin/env bash

set -e
set -x

poetry run black drifactorial tests --check
poetry run ruff drifactorial tests
poetry run mypy drifactorial
