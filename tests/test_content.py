"""Tests for plugin content files (README, manifest)."""
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
README_PATH = PLUGIN_ROOT / "README.md"


class TestReadmeFile:
    def test_file_exists(self):
        assert README_PATH.is_file()

    def test_mentions_mcp2cli(self):
        assert "mcp2cli" in README_PATH.read_text().lower()


class TestNoStaleToolArtifacts:
    def test_no_tools_directory(self):
        assert not (PLUGIN_ROOT / "tools").exists()

    def test_no_tool_prompt_files(self):
        prompts = PLUGIN_ROOT / "prompts"
        assert not prompts.exists()
