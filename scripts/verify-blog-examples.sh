#!/bin/bash
# Verify that blog code examples pass all tests
# Called from blog repo's pre-push hook
#
# Usage: BLOG_PATH=/path/to/blog ./scripts/verify-blog-examples.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check BLOG_PATH is set
if [ -z "$BLOG_PATH" ]; then
    echo "Error: BLOG_PATH environment variable not set"
    echo "Usage: BLOG_PATH=/path/to/blog $0"
    exit 1
fi

# Check blog path exists
if [ ! -d "$BLOG_PATH" ]; then
    echo "Error: Blog path does not exist: $BLOG_PATH"
    exit 1
fi

echo "=== Verifying blog code examples ==="
echo "Blog path: $BLOG_PATH"
echo "Project path: $PROJECT_DIR"
echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Extract exercises from blog
echo "Extracting exercises from blog..."
BLOG_PATH="$BLOG_PATH" uv run python extract_from_blog.py
echo ""

# Run tests
echo "Running tests..."
uv run pytest test/ -v --tb=short

echo ""
echo "=== All blog code examples verified ==="
