import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

HOOKS_PATH = str(Path(__file__).resolve().parent.parent / "hooks.py")
EXECUTE_PATH = str(Path(__file__).resolve().parent.parent / "execute.py")


def _import_hooks():
    spec = importlib.util.spec_from_file_location("hooks", HOOKS_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _import_execute():
    spec = importlib.util.spec_from_file_location("execute", EXECUTE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestHooksInstall:
    def test_install_calls_execute_main(self, monkeypatch):
        mod = _import_hooks()
        mock_execute = MagicMock()
        mock_execute.main.return_value = 0
        monkeypatch.setattr(mod, "_load_execute", lambda: mock_execute)
        result = mod.install()
        assert result == 0
        mock_execute.main.assert_called_once()

    def test_load_execute_returns_module(self):
        mod = _import_hooks()
        loaded = mod._load_execute()
        assert hasattr(loaded, "main")


class TestExecuteMain:
    def test_returns_zero_on_success(self, monkeypatch):
        mod = _import_execute()
        mock_run = MagicMock(returncode=0, stdout="mcp2cli 1.0.0")
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_run)
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        assert mod.main() == 0

    def test_returns_zero_with_uvx_fallback(self, monkeypatch):
        mod = _import_execute()
        mock_fail = MagicMock(returncode=1, stderr="pip failed")
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_fail)
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/uvx" if c == "uvx" else None)
        assert mod.main() == 0

    def test_returns_one_on_failure_no_uvx(self, monkeypatch):
        mod = _import_execute()
        mock_fail = MagicMock(returncode=1, stderr="pip failed")
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_fail)
        monkeypatch.setattr("shutil.which", lambda c: None)
        assert mod.main() == 1

    def test_detects_uvx_available(self, monkeypatch, capsys):
        mod = _import_execute()
        mock_run = MagicMock(returncode=0, stdout="ok")
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_run)
        monkeypatch.setattr("shutil.which", lambda c: "/usr/bin/" + c)
        mod.main()
        captured = capsys.readouterr()
        assert "uvx" in captured.out.lower() or "installed" in captured.out.lower()
