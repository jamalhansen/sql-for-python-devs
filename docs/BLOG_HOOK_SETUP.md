# Pre-Push Hook for SQL for Python Devs

This document explains how to set up a git pre-push hook that verifies your blog's SQL and Python code examples before pushing.

## What It Does

When you run `git push` in your blog repo, the hook automatically:

1. Extracts SQL and Python code blocks from your "SQL for Python Developers" blog posts
2. Runs 100+ tests to verify the code examples work correctly
3. Blocks the push if any tests fail

This ensures you never publish blog posts with broken code examples.

## Prerequisites

1. **sql-for-python-devs repo** cloned locally:
   ```bash
   git clone https://github.com/jamalhansen/sql-for-python-devs.git ~/projects/sql-for-python-devs
   ```

2. **uv** installed (Python package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Dependencies installed** in the test project:
   ```bash
   cd ~/projects/sql-for-python-devs
   uv sync
   ```

## Setup

### 1. Create the pre-push hook

Create the file `.git/hooks/pre-push` in your blog repo:

```bash
#!/bin/bash
# Pre-push hook: Verify SQL for Python Devs code examples
#
# This hook runs tests against code examples in blog posts
# before allowing a push. If tests fail, the push is blocked.

# Path to the sql-for-python-devs test project
# Adjust this path if your project is in a different location
TEST_PROJECT="$HOME/projects/sql-for-python-devs"

# Only run verification if the test project exists
if [ ! -d "$TEST_PROJECT" ]; then
    echo "Warning: sql-for-python-devs not found at $TEST_PROJECT"
    echo "Skipping blog code verification."
    echo "To enable verification, clone the repo:"
    echo "  git clone https://github.com/jamalhansen/sql-for-python-devs.git $TEST_PROJECT"
    exit 0
fi

# Check if verification script exists
VERIFY_SCRIPT="$TEST_PROJECT/scripts/verify-blog-examples.sh"
if [ ! -f "$VERIFY_SCRIPT" ]; then
    echo "Warning: Verification script not found at $VERIFY_SCRIPT"
    echo "Skipping blog code verification."
    exit 0
fi

echo "========================================"
echo "Verifying blog code examples..."
echo "========================================"
echo ""

# Run verification with current directory as blog path
BLOG_PATH="$(pwd)" "$VERIFY_SCRIPT"

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "ERROR: Blog code examples failed verification!"
    echo "========================================"
    echo ""
    echo "Fix the failing tests above before pushing."
    echo ""
    echo "To skip this check (not recommended), use:"
    echo "  git push --no-verify"
    echo ""
    exit 1
fi

echo ""
echo "Blog code verification passed!"
```

### 2. Make it executable

```bash
chmod +x .git/hooks/pre-push
```

### 3. Test the hook

Run a test push to verify everything works:

```bash
# This will trigger the hook
git push --dry-run
```

## Usage

Once set up, the hook runs automatically on every `git push`. You don't need to do anything special.

### Example output (success)

```
========================================
Verifying blog code examples...
========================================

Extracting exercises from blog...
✓ Extracted Python: 02_zero-setup-sql-run-your-first-sql-query.py
✓ Extracted SQL: 06_select-choosing-your-columns_1_1.sql
...

Running tests...
======================== 106 passed, 2 skipped in 2.24s ========================

Blog code verification passed!
```

### Example output (failure)

```
========================================
Verifying blog code examples...
========================================

Running tests...
FAILED test/test_sql_queries.py::TestSelectColumns::test_select_name_email
...

========================================
ERROR: Blog code examples failed verification!
========================================

Fix the failing tests above before pushing.
```

## Skipping the Hook

If you need to push without verification (e.g., non-code changes):

```bash
git push --no-verify
```

Use this sparingly—the hook exists to protect you from publishing broken code.

## Troubleshooting

### "sql-for-python-devs not found"

Clone the test project:
```bash
git clone https://github.com/jamalhansen/sql-for-python-devs.git ~/projects/sql-for-python-devs
cd ~/projects/sql-for-python-devs
uv sync
```

### "uv: command not found"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Tests fail but code looks correct

1. Make sure you've pulled the latest test project:
   ```bash
   cd ~/projects/sql-for-python-devs
   git pull
   uv sync
   ```

2. Run tests manually to see detailed output:
   ```bash
   cd ~/projects/sql-for-python-devs
   BLOG_PATH=/path/to/your/blog uv run pytest test/ -v
   ```

### Hook doesn't run

Check that the hook is executable:
```bash
ls -la .git/hooks/pre-push
# Should show -rwxr-xr-x
```

If not, run:
```bash
chmod +x .git/hooks/pre-push
```

## Sharing with Team Members

Git hooks are not committed to the repository. Each developer needs to set up the hook locally.

Options for sharing:

1. **Document it** (this file)
2. **Use a setup script** - Create a `scripts/setup-hooks.sh` that copies hooks into place
3. **Use a tool like husky or lefthook** - These tools manage git hooks via config files

### Example setup script

Add this to your blog repo as `scripts/setup-hooks.sh`:

```bash
#!/bin/bash
# Set up git hooks for this repository

HOOKS_DIR="$(git rev-parse --show-toplevel)/.git/hooks"

# Copy pre-push hook
cp "$(dirname "$0")/hooks/pre-push" "$HOOKS_DIR/pre-push"
chmod +x "$HOOKS_DIR/pre-push"

echo "Git hooks installed successfully!"
```

Then store the hook in `scripts/hooks/pre-push` and commit it to the repo.
