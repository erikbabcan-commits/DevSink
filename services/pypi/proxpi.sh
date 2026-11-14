#!/usr/bin/env bash
# DevSink ProxPi Launcher
# Runs high-performance WSGI Python package caching proxy on :5050
export PROXPI_CACHE_DIR="${DEVSINK_STORAGE:-/tmp}/pypi/storage"
export PROXPI_INDEX_URL="https://pypi.org/simple/"

mkdir -p "$PROXPI_CACHE_DIR"

if command -v uv >/dev/null 2>&1; then
    exec uv run --with proxpi --with gunicorn gunicorn --workers 2 --bind 0.0.0.0:5050 proxpi.server:app
else
    exec python3 -m gunicorn --workers 2 --bind 0.0.0.0:5050 proxpi.server:app
fi
