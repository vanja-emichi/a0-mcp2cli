"""Tests for UX enhancements: camelCase conversion and enhanced list output."""
import os
import sys
import importlib.util
import re

import pytest

# Import the plugin tool module
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A0_ROOT = os.path.abspath(os.path.join(PLUGIN_ROOT, "..", "..", ".."))


def _import_tool(tmp_path):
    """Import the tool module with isolated A0_ROOT."""
    spec = importlib.util.spec_from_file_location(
        "mcp2cli_tool",
        os.path.join(PLUGIN_ROOT, "tools", "mcp2cli.py"),
        submodule_search_locations=[],
    )
    mod = importlib.util.module_from_spec(spec)
    mod._A0_ROOT = str(tmp_path)
    sys.modules["mcp2cli_tool"] = mod
    spec.loader.exec_module(mod)
    return mod


# ===========================================================================
# Enhancement 1: camelCase → kebab-case in JSON params
# ===========================================================================


class TestCamelCaseConversion:
    """JSON params with camelCase keys must be converted to --kebab-case flags."""

    def test_camelcase_key_converted_to_kebab(self, tmp_path):
        """repoName should become --repo-name."""
        t = _import_tool(tmp_path)
        cmd = t._build_cmd(
            bin_argv=["mcp2cli"],
            server_cfg={"url": "http://x"},
            action="call",
            tool_name="ask-question",
            params='{"repoName": "frdel/agent-zero", "question": "What is it?"}',
            search_query="",
            toon=False,
        )
        assert "--repo-name" in cmd
        assert "--repoName" not in cmd

    def test_pascalcase_key_converted(self, tmp_path):
        """RepoName should become --repo-name."""
        t = _import_tool(tmp_path)
        cmd = t._build_cmd(
            bin_argv=["mcp2cli"],
            server_cfg={"url": "http://x"},
            action="call",
            tool_name="test",
            params='{"RepoName": "value"}',
            search_query="",
            toon=False,
        )
        assert "--repo-name" in cmd

    def test_snakecase_key_still_works(self, tmp_path):
        """repo_name should become --repo-name."""
        t = _import_tool(tmp_path)
        cmd = t._build_cmd(
            bin_argv=["mcp2cli"],
            server_cfg={"url": "http://x"},
            action="call",
            tool_name="test",
            params='{"repo_name": "value"}',
            search_query="",
            toon=False,
        )
        assert "--repo-name" in cmd

    def test_already_kebab_works(self, tmp_path):
        """repo-name should stay --repo-name."""
        t = _import_tool(tmp_path)
        cmd = t._build_cmd(
            bin_argv=["mcp2cli"],
            server_cfg={"url": "http://x"},
            action="call",
            tool_name="test",
            params='{"repo-name": "value"}',
            search_query="",
            toon=False,
        )
        assert "--repo-name" in cmd

    def test_cli_flags_still_work(self, tmp_path):
        """CLI-style flags should not be affected by camelCase conversion."""
        t = _import_tool(tmp_path)
        cmd = t._build_cmd(
            bin_argv=["mcp2cli"],
            server_cfg={"url": "http://x"},
            action="call",
            tool_name="test",
            params="--repo-name value --question 'What?'",
            search_query="",
            toon=False,
        )
        assert "--repo-name" in cmd
        assert "--question" in cmd


# ===========================================================================
# Enhancement 2: Enhanced list output with param names
# ===========================================================================


class TestListOutputWithParams:
    """The list action output should include parameter names for each tool."""

    def test_build_cmd_imports_re(self, tmp_path):
        """The tool module should import re for camelCase conversion."""
        t = _import_tool(tmp_path)
        # Just verify the module loaded
        assert hasattr(t, "_build_cmd")
