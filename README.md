# MCP2CLI Plugin for Agent Zero

Token-efficient CLI bridge to any MCP server. Lets agents discover and call tools on any configured MCP server without loading all schemas into context — saving **96–99% of tokens** compared to native MCP tool injection.

## Features

- 🔌 **Works with any MCP server** — stdio or HTTP/SSE
- 🗂️ **Auto-reads your settings** — uses MCP servers already configured in Agent Zero
- 🔍 **Discover tools on demand** — list, search, inspect without polluting context
- ⚡ **Ad-hoc connections** — connect to any MCP URL or stdio command directly
- 🪙 **Token savings** — only load what you need, when you need it
- 🔒 **Secret-safe** — credentials stay in env vars, not CLI arguments

## Installation

1. Enable the plugin in Agent Zero Settings → Agent tab
2. Click **Initialize** to install `mcp2cli` (or it falls back to `uvx mcp2cli` automatically)

## Usage

The plugin adds a `mcp2cli` tool to Agent Zero. Agents can:

```
# See all configured MCP servers
{ "tool_name": "mcp2cli", "tool_args": {} }

# List tools on a server
{ "tool_name": "mcp2cli", "tool_args": { "server": "gtm", "action": "list" } }

# Search tools
{ "tool_name": "mcp2cli", "tool_args": { "server": "gtm", "action": "search", "search_query": "tag" } }

# Inspect a tool's parameters
{ "tool_name": "mcp2cli", "tool_args": { "server": "gtm", "action": "help", "tool_name": "list-gtm-tags" } }

# Call a tool
{ "tool_name": "mcp2cli", "tool_args": { "server": "gtm", "action": "call", "tool_name": "list-gtm-tags", "params": "{\"account-id\": \"123\", \"container-id\": \"456\"}" } }

# Ad-hoc HTTP server
{ "tool_name": "mcp2cli", "tool_args": { "mcp_url": "https://mcp.deepwiki.com/mcp", "action": "list" } }
```

## Supported server types

| Type | Settings field | Example |
|---|---|---|
| stdio | `command` + `args` + `env` | `npx gtm-mcp` |
| HTTP/SSE | `url` + `type` | `https://mcp.deepwiki.com/mcp` |
| streamable-http | `url` + `type: streamable-http` | auto-detected |

## Requirements

- Python 3.10+
- `mcp2cli` (installed via Initialize) or `uvx` (zero-install fallback)
- Node.js (for stdio servers using `npx`)

## Token savings

Instead of injecting all MCP tool schemas into every LLM turn:

| Approach | Tokens/turn |
|---|---|
| Native MCP (all schemas) | ~5,000–20,000 |
| mcp2cli (on-demand) | ~100–300 |
| **Savings** | **96–99%** |
