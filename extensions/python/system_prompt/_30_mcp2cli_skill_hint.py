"""Inject a concise !!! rule: load mcp2cli skill before first MCP use."""
from helpers.extension import Extension

_LOADED_SKILLS_KEY = "loaded_skills"

_HINT = """## MCP2CLI
!!! when you need an MCP server tool, load skill **mcp2cli** via skills_tool first if not already in EXTRAS"""


class Mcp2cliSkillHint(Extension):

    async def execute(self, system_prompt: list = [], **kwargs):
        if not self.agent:
            return
        loaded = self.agent.data.get(_LOADED_SKILLS_KEY, [])
        if "mcp2cli" in loaded:
            return
        system_prompt.append(_HINT)
