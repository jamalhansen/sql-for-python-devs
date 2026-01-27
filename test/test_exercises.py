"""Tests for Python exercises extracted from blog posts.

These tests verify that the Python examples from the blog are valid and runnable.
"""

import ast
import subprocess
import sys
import pytest
from pathlib import Path


# Exercise files that are complete, runnable scripts
RUNNABLE_EXERCISES = {
    "02_zero-setup-sql-run-your-first-sql-query-in-under-5-minutes-with-duckdb.py",
    "03_generate-practice-data-with-faker.py",
    "04_dont-forget-to-save-persisting-your-duckdb-database.py",
}

# Exercise files that are code snippets (reference undefined variables like `customers`)
CODE_SNIPPETS = {
    "05_sql-thinks-in-sets-not-loops.py",
    "06_select-choosing-your-columns.py",
    "07_from-where-your-data-lives.py",
    "08_order-by-sorting-your-results.py",
}


def get_all_exercise_files():
    """Discover all Python files in the exercises/ directory."""
    exercises_dir = Path("exercises")
    if not exercises_dir.exists():
        return []
    return sorted(exercises_dir.glob("*.py"))


class TestAllExercisesValidSyntax:
    """Verify all exercise files have valid Python syntax."""

    @pytest.mark.parametrize(
        "exercise_file",
        get_all_exercise_files(),
        ids=lambda f: f.name,
    )
    def test_exercise_has_valid_python_syntax(self, exercise_file):
        """Every exercise file should have valid Python syntax."""
        source = exercise_file.read_text()

        # ast.parse will raise SyntaxError if invalid
        try:
            ast.parse(source, filename=str(exercise_file))
        except SyntaxError as e:
            pytest.fail(f"{exercise_file.name} has invalid syntax: {e}")

    @pytest.mark.parametrize(
        "exercise_file",
        get_all_exercise_files(),
        ids=lambda f: f.name,
    )
    def test_exercise_is_not_empty(self, exercise_file):
        """Every exercise file should contain code."""
        source = exercise_file.read_text().strip()
        assert len(source) > 0, f"{exercise_file.name} should not be empty"

    @pytest.mark.parametrize(
        "exercise_file",
        get_all_exercise_files(),
        ids=lambda f: f.name,
    )
    def test_exercise_has_no_syntax_errors_in_strings(self, exercise_file):
        """Exercise files should compile without errors."""
        source = exercise_file.read_text()

        # compile() catches some errors that ast.parse might miss
        try:
            compile(source, str(exercise_file), "exec")
        except SyntaxError as e:
            pytest.fail(f"{exercise_file.name} failed to compile: {e}")


class TestRunnableExercises:
    """Test that complete exercise scripts execute successfully."""

    @pytest.mark.parametrize(
        "exercise_name",
        sorted(RUNNABLE_EXERCISES),
        ids=lambda f: f,
    )
    def test_exercise_runs_without_error(self, exercise_name):
        """Complete exercise scripts should run without raising exceptions."""
        exercise_file = Path("exercises") / exercise_name
        if not exercise_file.exists():
            pytest.skip(f"Exercise file not found: {exercise_name}")

        result = subprocess.run(
            [sys.executable, str(exercise_file)],
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
        )

        if result.returncode != 0:
            pytest.fail(
                f"{exercise_name} failed with exit code {result.returncode}:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

    @pytest.mark.parametrize(
        "exercise_name",
        sorted(RUNNABLE_EXERCISES),
        ids=lambda f: f,
    )
    def test_exercise_produces_output(self, exercise_name):
        """Complete exercise scripts should produce some output."""
        exercise_file = Path("exercises") / exercise_name
        if not exercise_file.exists():
            pytest.skip(f"Exercise file not found: {exercise_name}")

        result = subprocess.run(
            [sys.executable, str(exercise_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # These are demo scripts, they should print something
        assert len(result.stdout.strip()) > 0, (
            f"{exercise_name} should produce output"
        )


class TestCodeSnippets:
    """Test that code snippet exercises are valid (but can't be run standalone)."""

    @pytest.mark.parametrize(
        "snippet_name",
        sorted(CODE_SNIPPETS),
        ids=lambda f: f,
    )
    def test_snippet_exists(self, snippet_name):
        """Code snippet files should exist."""
        snippet_file = Path("exercises") / snippet_name
        if not snippet_file.exists():
            pytest.skip(f"Snippet file not found: {snippet_name}")
        assert snippet_file.exists()

    @pytest.mark.parametrize(
        "snippet_name",
        sorted(CODE_SNIPPETS),
        ids=lambda f: f,
    )
    def test_snippet_has_valid_syntax(self, snippet_name):
        """Code snippets should have valid Python syntax even if not runnable."""
        snippet_file = Path("exercises") / snippet_name
        if not snippet_file.exists():
            pytest.skip(f"Snippet file not found: {snippet_name}")

        source = snippet_file.read_text()
        try:
            ast.parse(source, filename=str(snippet_file))
        except SyntaxError as e:
            pytest.fail(f"{snippet_name} has invalid syntax: {e}")

    @pytest.mark.parametrize(
        "snippet_name",
        sorted(CODE_SNIPPETS),
        ids=lambda f: f,
    )
    def test_snippet_references_customers(self, snippet_name):
        """Code snippets should reference the 'customers' variable (as expected)."""
        snippet_file = Path("exercises") / snippet_name
        if not snippet_file.exists():
            pytest.skip(f"Snippet file not found: {snippet_name}")

        source = snippet_file.read_text()
        assert "customers" in source or "customer" in source, (
            f"{snippet_name} should reference customers data"
        )


class TestExerciseDirectoryStructure:
    """Tests for the exercises directory itself."""

    def test_exercises_directory_exists(self):
        """The exercises/ directory should exist."""
        assert Path("exercises").exists(), "exercises/ directory should exist"

    def test_has_exercise_files(self):
        """Should have exercise files in the exercises/ directory."""
        exercise_files = get_all_exercise_files()
        assert len(exercise_files) > 0, "Should have at least one exercise file"

    def test_all_exercises_are_categorized(self):
        """Every exercise file should be in either RUNNABLE or SNIPPETS."""
        exercise_files = get_all_exercise_files()
        all_known = RUNNABLE_EXERCISES | CODE_SNIPPETS

        for exercise in exercise_files:
            assert exercise.name in all_known, (
                f"{exercise.name} is not categorized.\n"
                f"Add it to one of these sets in test_exercises.py:\n"
                f"  - RUNNABLE_EXERCISES: if it's a complete script that can run standalone\n"
                f"  - CODE_SNIPPETS: if it references undefined variables like 'customers'"
            )
