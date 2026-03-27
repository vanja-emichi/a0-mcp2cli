### mcp2cli:
Token-efficient CLI bridge to any MCP server. Instead of loading all MCP tool schemas into context, use this tool to discover and call individual tools on demand — saving 96-99% of tokens.

Supports all MCP servers configured in Agent Zero settings (stdio or HTTP), plus ad-hoc connections via URL or command.

#### Arguments
- `server` (string) — name of a configured MCP server (e.g. `gtm`, `deep-wiki`). Leave empty to see all configured servers.
- `action` (string) — one of:
  - `servers` — list all configured MCP servers with their status (default when no server given)
  - `list` — list all tools available on the server
  - `search` — search tools by name/description (requires `search_query`)
  - `help` — show parameters for a specific tool (requires `tool_name`)
  - `call` — call a specific tool (requires `tool_name`, optionally `params`)
- `tool_name` (string) — tool to inspect or call (for `help` and `call` actions)
- `params` (string) — tool arguments as a JSON object `{"key": "value"}` or raw CLI flags `--key value`
- `search_query` (string) — keyword to search tools by (for `search` action)
- `mcp_url` (string) — ad-hoc HTTP/SSE MCP server URL (overrides `server`)
- `mcp_stdio` (string) — ad-hoc stdio command e.g. `npx some-mcp-server` (overrides `server`)
- `mcp_env` (string) — comma-separated env vars for stdio servers e.g. `KEY=val,KEY2=val2`
- `toon` (string) — `true` to use TOON token-efficient encoding for large list outputs

#### Recommended workflow
1. First call with no args to see configured servers
2. `action=list` to discover tools on a server
3. `action=help` with `tool_name` to see parameters
4. `action=call` with `tool_name` and `params` to execute

#### Usage examples

##### List all configured MCP servers
~~~json
{
    "thoughts": ["Let me see what MCP servers are available"],
    "tool_name": "mcp2cli",
    "tool_args": {}
}
~~~

##### List all tools on the GTM server
~~~json
{
    "thoughts": ["Discover what tools GTM server offers"],
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "gtm",
        "action": "list"
    }
}
~~~

##### Search for tag-related tools
~~~json
{
    "thoughts": ["Find tag tools on GTM server"],
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "gtm",
        "action": "search",
        "search_query": "tag"
    }
}
~~~

##### Inspect a tool's parameters
~~~json
{
    "thoughts": ["Check parameters for list-gtm-tags"],
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "gtm",
        "action": "help",
        "tool_name": "list-gtm-tags"
    }
}
~~~

##### Call a tool with JSON params
~~~json
{
    "thoughts": ["List GTM tags for this account and container"],
    "tool_name": "mcp2cli",
    "tool_args": {
        "server": "gtm",
        "action": "call",
        "tool_name": "list-gtm-tags",
        "params": "{\"account-id\": \"123456\", \"container-id\": \"789\"}"
    }
}
~~~

##### Connect to an ad-hoc HTTP MCP server
~~~json
{
    "thoughts": ["Connect to deep-wiki MCP directly by URL"],
    "tool_name": "mcp2cli",
    "tool_args": {
        "mcp_url": "https://mcp.deepwiki.com/mcp",
        "action": "list"
    }
}
~~~

##### Connect to an ad-hoc stdio MCP server
~~~json
{
    "thoughts": ["Use a stdio MCP server directly"],
    "tool_name": "mcp2cli",
    "tool_args": {
        "mcp_stdio": "npx some-mcp-server",
        "mcp_env": "API_KEY=sk-abc,DEBUG=1",
        "action": "list"
    }
}
~~~
