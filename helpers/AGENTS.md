# helpers/ DOX

## Purpose
`mcp_servers.py` — resolves configured (typically `disabled: true`) MCP server
connection strings + credentials from A0 settings into ready-to-use `uvx mcp2cli` commands.

## Local Contracts
- Location-independent: resolves the `/a0` root automatically; works from `plugins/` and `usr/plugins/`.
- Stdlib-first: executed by the agent via `code_execution_tool` in the `/opt/venv` (3.13) runtime — no framework imports allowed in the CLI path.
- Never print secret values; redact credentials in output.

## Verification
`docker exec agent-zero-loloi /opt/venv/bin/python /a0/usr/plugins/mcp2cli/helpers/mcp_servers.py` (lists configured servers).
