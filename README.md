# MCP2CLI — Agent Zero Plugin

Token-efficient CLI bridge to any MCP server. Instead of injecting all MCP tool schemas into every LLM turn, agents discover and call tools **on demand** — saving **96–99% of tokens** compared to native MCP injection.

---

## The Problem with Native MCP in Agent Zero

When you add MCP servers to Agent Zero's settings and leave them **enabled**, the framework injects **all tool schemas** from every server into the system prompt on every single turn. A typical MCP server exposes 20–50 tools, each with a full JSON schema description.

| Approach | Tokens per turn | Impact |
|---|---|---|
| Native MCP (enabled) | 5,000–20,000 | Pollutes context every turn |
| **mcp2cli (disabled + on-demand)** | **100–300** | Only what you ask for |
| mcp2cli + `toon` encoding | 60–180 | Maximum efficiency |

**The solution:** configure your MCP servers in Agent Zero settings but set them to `"disabled": true`. This keeps their connection details available for `mcp2cli` to use, without injecting their schemas into context.

---

## Setup

### Step 1 — Install the Plugin

1. Enable **MCP2CLI** in Agent Zero → Settings → Agent tab
2. Click **Initialize** to install the `mcp2cli` binary
   - Falls back to `uvx mcp2cli` automatically if pip install fails
   - No extra steps needed if `uvx` is available

### Step 2 — Configure MCP Servers (with `disabled: true`)

Open Agent Zero → Settings → MCP tab and add your servers. The key is to set **`"disabled": true`** on each server so their schemas are **not** injected into the system prompt, while their connection config remains available to the `mcp2cli` tool.

Example `mcpServers` configuration in Agent Zero settings:

```json
{
  "mcpServers": {
    "gtm": {
      "command": "npx",
      "args": ["gtm-mcp"],
      "env": {
        "GTM_CREDENTIALS_FILE": "/path/to/credentials.json",
        "GTM_TOKEN_FILE": "/path/to/token.json"
      },
      "disabled": true
    },
    "deep-wiki": {
      "url": "https://mcp.deepwiki.com/mcp",
      "type": "streamable-http",
      "disabled": true
    }
  }
}
```

> ⚠️ **`"disabled": true` is the key setting.** It tells Agent Zero to skip native schema injection for that server. The `mcp2cli` tool reads the same config and connects on demand — you get all the functionality with none of the context pollution.

### Step 3 — Use the `mcp2cli` Tool

Agents automatically have access to the `mcp2cli` tool. The plugin injects a skill hint into the system prompt reminding agents to load the `mcp2cli` skill for detailed usage instructions.

---

## Usage Workflow

Always follow this 4-step discovery pattern — never assume tool names:

### 1. See configured servers

```json
{
    "tool_name": "mcp2cli",
    "tool_args": {}
}
```

### 2. List tools on a server

```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "gtm",
        "action": "list"
    }
}
```

Or search by keyword:

```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "gtm",
        "action": "search",
        "search_query": "tag"
    }
}
```

### 3. Inspect a tool's parameters

```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "gtm",
        "action": "help",
        "tool_name": "list-gtm-tags"
    }
}
```

### 4. Call the tool

```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "gtm",
        "action": "call",
        "tool_name": "list-gtm-tags",
        "params": "{\"account-id\": \"123456\", \"container-id\": \"789\"}"
    }
}
```

---

## Ad-hoc Connections

Connect to any MCP server without pre-configuring it in settings:

```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "mcp_url": "https://mcp.deepwiki.com/mcp",
        "action": "list"
    }
}
```

```json
{
    "tool_name": "mcp2cli",
    "tool_args": {
        "mcp_stdio": "npx some-mcp-server",
        "mcp_env": "API_KEY=sk-abc,DEBUG=1",
        "action": "list"
    }
}
```

---

## Tool Arguments Reference

| Argument | Type | Description |
|---|---|---|
| `server` | string | Name of a configured server (from settings). Leave empty to list all servers. |
| `action` | string | `servers` \| `list` \| `search` \| `help` \| `call` |
| `tool_name` | string | Tool to inspect or call (for `help` / `call`) |
| `params` | string | JSON object `{"key": "val"}` or CLI flags `--key val` |
| `search_query` | string | Keyword to filter tools (for `search`) |
| `mcp_url` | string | Ad-hoc HTTP/SSE MCP server URL (overrides `server`) |
| `mcp_stdio` | string | Ad-hoc stdio command e.g. `npx some-mcp-server` (overrides `server`) |
| `mcp_env` | string | Comma-separated env vars for stdio: `KEY=val,KEY2=val2` |
| `toon` | string | `"true"` for TOON encoding — 40–60% fewer tokens on large list outputs |

---

## Supported Server Types

| Type | Config fields | Example |
|---|---|---|
| stdio | `command` + `args` + `env` | `npx gtm-mcp` |
| HTTP/SSE | `url` + `type: sse` | `https://mcp.example.com/sse` |
| Streamable HTTP | `url` + `type: streamable-http` | `https://mcp.deepwiki.com/mcp` |

---

## Requirements

- Agent Zero with MCP support
- `mcp2cli` binary (installed via Initialize) **or** `uvx` (zero-install fallback)
- Node.js (only for stdio servers using `npx`)

---

## License

MIT — see [LICENSE](LICENSE)
