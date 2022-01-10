#!/usr/bin/env bash

set -e
set -x

poetry run mypy drifactorial
poetry run flake8 drifactorial tests
poetry run black drifactorial tests --check
poetry run isort drifactorial tests --check-only
poetry run pydocstyle drifactorial
