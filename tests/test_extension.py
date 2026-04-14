import asyncio
import importlib
from pathlib import Path
from unittest.mock import MagicMock

import pytest

EXT_PATH = str(
    Path(__file__).resolve().parent.parent
    / "extensions" / "python" / "system_prompt"
    / "_30_mcp2cli_skill_hint.py"
)


def _import_ext():
    spec = importlib.util.spec_from_file_location("ext", EXT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSkillHintInjection:
    @pytest.mark.asyncio
    async def test_hint_appended_when_skill_not_loaded(self):
        mod = _import_ext()
        ext = mod.Mcp2cliSkillHint()
        ext.agent = MagicMock()
        ext.agent.data = {"loaded_skills": []}
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        assert len(system_prompt) == 1
        assert "mcp2cli" in system_prompt[0].lower()
        assert "skills_tool" in system_prompt[0]

    @pytest.mark.asyncio
    async def test_hint_skipped_when_skill_already_loaded(self):
        mod = _import_ext()
        ext = mod.Mcp2cliSkillHint()
        ext.agent = MagicMock()
        ext.agent.data = {"loaded_skills": ["mcp2cli"]}
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        assert len(system_prompt) == 0

    @pytest.mark.asyncio
    async def test_hint_skipped_when_no_agent(self):
        mod = _import_ext()
        ext = mod.Mcp2cliSkillHint()
        ext.agent = None
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        assert len(system_prompt) == 0

    @pytest.mark.asyncio
    async def test_hint_not_appended_to_existing_content(self):
        mod = _import_ext()
        ext = mod.Mcp2cliSkillHint()
        ext.agent = MagicMock()
        ext.agent.data = {"loaded_skills": []}
        system_prompt = ["existing content"]
        await ext.execute(system_prompt=system_prompt)
        assert len(system_prompt) == 2
        assert system_prompt[0] == "existing content"

    @pytest.mark.asyncio
    async def test_hint_contains_key_phrases(self):
        mod = _import_ext()
        ext = mod.Mcp2cliSkillHint()
        ext.agent = MagicMock()
        ext.agent.data = {"loaded_skills": []}
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        hint = system_prompt[0]
        assert "MCP2CLI" in hint
        assert "load" in hint.lower()
        assert "skill" in hint.lower()

    @pytest.mark.asyncio
    async def test_hint_skipped_when_other_skill_loaded(self):
        mod = _import_ext()
        ext = mod.Mcp2cliSkillHint()
        ext.agent = MagicMock()
        ext.agent.data = {"loaded_skills": ["playwright-cli"]}
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        assert len(system_prompt) == 1

    @pytest.mark.asyncio
    async def test_hint_skipped_when_loaded_skills_key_missing(self):
        mod = _import_ext()
        ext = mod.Mcp2cliSkillHint()
        ext.agent = MagicMock()
        ext.agent.data = {}
        system_prompt = []
        await ext.execute(system_prompt=system_prompt)
        assert len(system_prompt) == 1
