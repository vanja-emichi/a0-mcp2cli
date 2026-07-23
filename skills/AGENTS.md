# skills/ DOX

## Purpose
`mcp2cli/SKILL.md` — teaches the agent the discover → inspect → call workflow via
`code_execution_tool` + `uvx mcp2cli`, using `helpers/mcp_servers.py` for config resolution.

## Local Contracts
- Keep token cost minimal: the skill exists to avoid schema injection; do not reintroduce per-server schemas.
- Commands must reference `helpers/mcp_servers.py` for connection details, never hardcoded credentials.
