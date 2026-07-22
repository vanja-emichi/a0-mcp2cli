"""Tests for the mcp2cli system-prompt extension using the real framework."""
import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

EXT_PATH = Path(__file__).resolve().parent.parent / "extensions" / "python" / "system_prompt" / "_30_mcp2cli_skill_hint.py"
_PROJECT_ROOT = EXT_PATH.parents[5]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _import_ext():
    spec = importlib.util.spec_from_file_location("ext", str(EXT_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_ext(mod):
    """Build an extension with a stub agent (agent is the only required arg)."""
    agent = MagicMock()
    agent.data = {"loaded_skills": []}
    return mod.Mcp2cliSkillHint(agent)


class TestSkillHintInjection:
    @pytest.mark.asyncio
    async def test_hint_appended_when_skill_not_loaded(self):
        mod = _import_ext()
        ext = _make_ext(mod)
        ext.agent.data = {"loaded_skills": []}
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        assert len(system_prompt) == 1
        assert "mcp2cli" in system_prompt[0].lower()
        assert "skills_tool" in system_prompt[0]

    @pytest.mark.asyncio
    async def test_hint_skipped_when_skill_already_loaded(self):
        mod = _import_ext()
        ext = _make_ext(mod)
        ext.agent.data = {"loaded_skills": ["mcp2cli"]}
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        assert system_prompt == []

    @pytest.mark.asyncio
    async def test_hint_not_appended_to_existing_content(self):
        mod = _import_ext()
        ext = _make_ext(mod)
        ext.agent.data = {"loaded_skills": []}
        system_prompt = ["existing prompt content"]
        await ext.execute(system_prompt=system_prompt)
        assert len(system_prompt) == 2
        assert system_prompt[0] == "existing prompt content"
        assert "mcp2cli" in system_prompt[1].lower()

    @pytest.mark.asyncio
    async def test_hint_contains_key_phrases(self):
        mod = _import_ext()
        ext = _make_ext(mod)
        ext.agent.data = {"loaded_skills": []}
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        hint = system_prompt[0]
        assert "mcp2cli" in hint.lower()
        assert "skills_tool" in hint
        assert "load skill" in hint.lower()

    @pytest.mark.asyncio
    async def test_hint_skipped_when_other_skill_loaded(self):
        mod = _import_ext()
        ext = _make_ext(mod)
        ext.agent.data = {"loaded_skills": ["some_other_skill"]}
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        assert len(system_prompt) == 1  # mcp2cli not loaded -> hint still added

    @pytest.mark.asyncio
    async def test_hint_skipped_when_loaded_skills_key_missing(self):
        mod = _import_ext()
        ext = _make_ext(mod)
        # data dict has no loaded_skills key at all
        ext.agent.data = {}
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        assert len(system_prompt) == 1
