#!/usr/bin/env bash
# ==============================================================================
#  ⚡ DevSink Cache Auto-Pruner
# ==============================================================================
#  Keeps the DevSink storage within target disk limits (default: 80% capacity).
#  Prunes oldest cached npm tarballs and pypi wheels if disk threshold is exceeded.
# ==============================================================================

set -e

STORAGE_DIR="${DEVSINK_STORAGE:-/home/vorkei/black-hole-cache}"
MAX_USAGE_PERCENT="${MAX_USAGE_PERCENT:-80}"

echo "🧹 Checking DevSink storage usage on: $STORAGE_DIR"

if [ ! -d "$STORAGE_DIR" ]; then
    echo "Storage dir $STORAGE_DIR does not exist. Exiting."
    exit 0
fi

# Get current usage percentage of the filesystem hosting the storage
CURRENT_PERCENT=$(df -P "$STORAGE_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
echo "Current disk usage: ${CURRENT_PERCENT}% (Threshold: ${MAX_USAGE_PERCENT}%)"

if [ "$CURRENT_PERCENT" -gt "$MAX_USAGE_PERCENT" ]; then
    echo "⚠️ Disk usage exceeds ${MAX_USAGE_PERCENT}%. Starting LRU cache eviction..."

    # Prune npm cache (files older than 30 days)
    if [ -d "$STORAGE_DIR/npm/storage" ]; then
        echo "Pruning npm cached packages older than 30 days..."
        find "$STORAGE_DIR/npm/storage" -type f -name "*.tgz" -atime +30 -delete 2>/dev/null || true
    fi

    # Prune PyPI wheel cache
    if [ -d "$STORAGE_DIR/pypi/storage" ]; then
        echo "Pruning PyPI wheels older than 30 days..."
        find "$STORAGE_DIR/pypi/storage" -type f \( -name "*.whl" -o -name "*.tar.gz" \) -atime +30 -delete 2>/dev/null || true
    fi

    NEW_PERCENT=$(df -P "$STORAGE_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    echo "✅ Eviction complete. New disk usage: ${NEW_PERCENT}%"
else
    echo "✅ Disk usage is well within safe thresholds. No eviction needed."
fi
