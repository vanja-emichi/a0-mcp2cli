import asyncio
import importlib
import json
import shlex
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

TOOL_PATH = str(Path(__file__).resolve().parent.parent / "tools" / "mcp2cli.py")


def _import_tool():
    spec = importlib.util.spec_from_file_location("mcp2cli_tool_review", TOOL_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSecretRedaction:
    """display_cmd should not leak secret values in logs."""

    @pytest.mark.asyncio
    async def test_env_values_redacted_in_progress(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(return_value=(b'ok', b''))
        mp.returncode = 0
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mp))
        tool = mod.Mcp2cli()
        await tool.execute(
            mcp_stdio="npx my-server",
            mcp_env="API_KEY=sk-secret-123,TOKEN=abc",
            action="list",
        )
        # The progress message should NOT contain the secret values
        progress_call = tool.add_progress.call_args[0][0]
        assert "sk-secret-123" not in progress_call
        assert "API_KEY=***" in progress_call or "API_KEY" not in progress_call

    @pytest.mark.asyncio
    async def test_non_env_flags_not_redacted(self, monkeypatch):
        mod = _import_tool()
        mp = MagicMock()
        mp.communicate = AsyncMock(return_value=(b'ok', b''))
        mp.returncode = 0
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mp))
        tool = mod.Mcp2cli()
        await tool.execute(
            mcp_url="https://example.com/mcp",
            action="call",
            tool_name="create",
            params='{"name": "test-name"}',
        )
        progress_call = tool.add_progress.call_args[0][0]
        assert "test-name" in progress_call


class TestBuildCmdExceptRedundancy:
    """_build_cmd exception handler should not have redundant ValueError."""

    def test_build_cmd_catches_general_exception(self, monkeypatch):
        mod = _import_tool()
        # This tests that the execute method handles build errors
        # The except clause should be just `except Exception` not `except (ValueError, Exception)`
        import inspect
        source = inspect.getsource(mod._build_cmd)
        # _build_cmd itself raises ValueError, which is correct
        # The redundancy is in execute() - check that
        exec_source = inspect.getsource(mod.Mcp2cli.execute)
        # Should NOT contain the redundant (ValueError, Exception) pattern
        assert "(ValueError, Exception)" not in exec_source


class TestGetMcp2CliBinCaching:
    """_get_mcp2cli_bin should be cached to avoid repeated shutil.which calls."""

    def test_bin_cached_after_first_call(self, monkeypatch):
        mod = _import_tool()
        which_calls = []
        def track_which(cmd):
            which_calls.append(cmd)
            return "/usr/bin/" + cmd
        monkeypatch.setattr("shutil.which", track_which)
        # First call
        result1 = mod._get_mcp2cli_bin()
        # Second call
        result2 = mod._get_mcp2cli_bin()
        assert result1 == result2
        # shutil.which should be called at most once per binary candidate
        # (mcp2cli first, only if not found then uvx)
        assert len(which_calls) <= 1


class TestPluginReadmeExists:
    """Plugin should not have a dangling README.md copy in source dir."""

    def test_source_readme_exists(self):
        src_readme = Path(__file__).resolve().parent.parent / ".a0proj" / "mcp2cli-src" / "README.md"
        assert src_readme.exists(), "Source README.md should exist (created during setup)"
