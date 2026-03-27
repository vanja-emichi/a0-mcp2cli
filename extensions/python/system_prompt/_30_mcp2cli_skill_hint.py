"""Inject a concise !!! rule: load mcp2cli skill before first use."""
from helpers.extension import Extension

# mirrors DATA_NAME_LOADED_SKILLS from tools/skills_tool.py
_LOADED_SKILLS_KEY = "loaded_skills"

_HINT = """## MCP2CLI
!!! when using mcp2cli tool, load skill **mcp2cli** via skills_tool first if not already in EXTRAS"""


class Mcp2cliSkillHint(Extension):

    async def execute(self, system_prompt: list = [], **kwargs):
        if not self.agent:
            return
        # Skip hint if skill is already loaded in EXTRAS this session
        loaded = self.agent.data.get(_LOADED_SKILLS_KEY, [])
        if "mcp2cli" in loaded:
            return
        system_prompt.append(_HINT)
