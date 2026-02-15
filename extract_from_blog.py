#!/usr/bin/env python3
"""
Extract Python code blocks from Hugo blog posts with specific series tag.
Filters posts by series and outputs numbered exercise files.
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional
import frontmatter


def get_series_posts(blog_dir: Path, series_name: str) -> list[tuple[Path, int]]:
    """
    Find all blog posts in a series, sorted by weight/order.

    Returns:
        List of (post_path, weight) tuples sorted by weight
    """
    blog_content_dir = blog_dir / "content" / "blog"
    posts_with_weight = []

    if not blog_content_dir.exists():
        print(f"Error: Blog content directory not found at {blog_content_dir}")
        return []

    for post_dir in blog_content_dir.iterdir():
        if not post_dir.is_dir():
            continue

        index_md = post_dir / "index.md"
        if not index_md.exists():
            continue

        post = frontmatter.load(index_md)

        # Check if post is in the specified series
        series_list = post.get("series", [])
        if isinstance(series_list, list):
            in_series = any(series_name.lower() in str(s).lower() for s in series_list)
        else:
            in_series = series_name.lower() in str(series_list).lower()

        if in_series:
            weight = post.get("weight", 999)  # Default weight if not specified
            posts_with_weight.append((index_md, weight))

    # Sort by weight
    posts_with_weight.sort(key=lambda x: x[1])
    return posts_with_weight


def extract_code_blocks(content: str, language: str = "python") -> list[str]:
    """Extract all code blocks of specified language from content."""
    # Matches ```python ... ``` blocks (or any language)
    pattern = rf"```{language}\n(.*?)```"
    blocks = re.findall(pattern, content, re.DOTALL)
    return blocks


def slugify(text: str) -> str:
    """Convert title to slug format."""
    return (
        text.lower()
        .replace(" ", "-")
        .replace(":", "")
        .replace("?", "")
        .replace("!", "")
        .replace(",", "")
        .replace("/", "-")
        .replace("'", "")
        .replace('"', "")
    )


def split_sql_by_comments(sql_content: str) -> list[str]:
    """
    Split SQL content by comment lines.

    Groups queries separated by comment lines starting with '--'.
    CTE queries (starting with WITH) are kept intact since their
    inline comments are annotations, not query separators.
    """
    stripped_content = sql_content.strip()

    # CTE queries are a single statement — don't split them
    if stripped_content.upper().startswith("WITH"):
        return [stripped_content]

    lines = stripped_content.split("\n")
    queries = []
    current_query = []

    for line in lines:
        stripped = line.strip()

        # If it's a comment and we have accumulated query lines
        if stripped.startswith("--") and current_query:
            # Save the current query
            query_text = "\n".join(current_query).strip()
            if query_text:
                queries.append(query_text)
            current_query = []
        elif stripped and not stripped.startswith("--"):
            # Add non-comment, non-empty lines to current query
            current_query.append(line)

    # Don't forget the last query
    if current_query:
        query_text = "\n".join(current_query).strip()
        if query_text:
            queries.append(query_text)

    return queries


def extract_series_exercises(
    blog_dir: Path,
    series_name: str,
    output_dir: Path,
    code_block_index: int = 0,
) -> None:
    """
    Extract exercises from blog posts in a series.

    Saves both Python and SQL code blocks separately.

    Args:
        blog_dir: Path to Hugo blog root
        series_name: Series tag to filter by
        output_dir: Directory to save extracted exercises
        code_block_index: Which Python code block to extract (0=first, 1=second, etc)
    """
    posts = get_series_posts(blog_dir, series_name)

    if not posts:
        print(f"No posts found in series '{series_name}'")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    sql_dir = output_dir.parent / "sql"
    sql_dir.mkdir(parents=True, exist_ok=True)

    # Clean old extracted files before re-extracting
    for old_file in output_dir.glob("*.py"):
        old_file.unlink()
    for old_file in sql_dir.glob("*.sql"):
        old_file.unlink()

    for idx, (post_path, weight) in enumerate(posts, 1):
        post = frontmatter.load(post_path)
        content = post.content
        title = post.get("title", f"Exercise {idx}")
        slug = slugify(title)

        # Extract Python code blocks
        py_blocks = extract_code_blocks(content, "python")

        if py_blocks and code_block_index < len(py_blocks):
            py_code = py_blocks[code_block_index]
            py_file = output_dir / f"{idx:02d}_{slug}.py"
            py_file.write_text(py_code)
            print(f"✓ Extracted Python: {py_file.name}")
        else:
            if not py_blocks:
                print(f"⚠️  No Python code blocks found in: {title}")

        # Extract SQL code blocks (save all of them)
        sql_blocks = extract_code_blocks(content, "sql")
        if sql_blocks:
            # Save all SQL blocks for this exercise
            for sql_idx, sql_block in enumerate(sql_blocks, 1):
                # Split multiple queries by comments
                queries = split_sql_by_comments(sql_block)

                for query_idx, query in enumerate(queries, 1):
                    # Create filename based on number of queries
                    if len(sql_blocks) == 1 and len(queries) == 1:
                        sql_file = sql_dir / f"{idx:02d}_{slug}.sql"
                    elif len(sql_blocks) == 1:
                        sql_file = sql_dir / f"{idx:02d}_{slug}_{query_idx}.sql"
                    else:
                        sql_file = (
                            sql_dir / f"{idx:02d}_{slug}_{sql_idx}_{query_idx}.sql"
                        )

                    sql_file.write_text(query)
                    print(f"✓ Extracted SQL: {sql_file.name}")

    print(f"\n✅ Extracted exercises to {output_dir} and {sql_dir}")


def main() -> None:
    """Main entry point for the extraction script."""
    # Configuration - use environment variable or default
    blog_path_str = os.environ.get("BLOG_PATH", "")
    if not blog_path_str:
        print("Error: BLOG_PATH environment variable not set.")
        print("Usage: BLOG_PATH=/path/to/hugo/blog python extract_from_blog.py [code_block_index]")
        sys.exit(1)

    blog_path = Path(blog_path_str)
    if not blog_path.exists():
        print(f"Error: Blog path does not exist: {blog_path}")
        sys.exit(1)

    series = "SQL for Python Developers"
    # Output to exercises/ directory relative to this script
    script_dir = Path(__file__).parent
    output_path = script_dir / "exercises"

    # Optional: specify which code block to extract (0-indexed)
    code_block_num = 0

    if len(sys.argv) > 1:
        try:
            code_block_num = int(sys.argv[1])
        except ValueError:
            print(f"Error: code_block_index must be an integer, got: {sys.argv[1]}")
            print("Usage: BLOG_PATH=/path/to/hugo/blog python extract_from_blog.py [code_block_index]")
            sys.exit(1)

    extract_series_exercises(blog_path, series, output_path, code_block_num)


if __name__ == "__main__":
    main()
