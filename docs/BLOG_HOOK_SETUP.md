# Blog Pre-Push Hook Setup

Verifies blog code examples before pushing.

## Prerequisites

```bash
# 1. Clone this repo
git clone https://github.com/jamalhansen/sql-for-python-devs.git ~/projects/sql-for-python-devs

# 2. Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
cd ~/projects/sql-for-python-devs && uv sync
```

## Install Hook

From your blog repo:

```bash
cp ~/projects/sql-for-python-devs/scripts/hooks/pre-push .git/hooks/
chmod +x .git/hooks/pre-push
```

## Usage

- Runs automatically on `git push`
- Skip with `git push --no-verify`

## Troubleshooting

```bash
# Run tests manually
cd ~/projects/sql-for-python-devs
BLOG_PATH=/path/to/blog uv run pytest test/ -v

# Update test project
cd ~/projects/sql-for-python-devs && git pull && uv sync
```
