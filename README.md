# Weather Alerts MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that gives AI assistants such as Claude access to live US weather alerts from the [National Weather Service API](https://www.weather.gov/documentation/services-web-api).

Once connected, you can ask an assistant something like *"Are there any weather alerts in California right now?"* It calls this server, gets the current alerts from the National Weather Service, and answers with up-to-date information.

## Features

- **`get_alerts` tool:** returns active weather alerts for any US state, given its two-letter code (e.g. `CA`, `TX`, `NY`). For each alert it shows:
  - Event type
  - Affected area
  - Severity
  - Description
  - Safety instructions
- **Async HTTP requests:** uses `httpx` with a 30-second timeout and error handling, so a failed or slow API call returns a clear message instead of crashing the server.
- **Standard MCP over stdio:** works with any MCP-compatible client, including Claude Desktop, Claude Code and the MCP Inspector.

## Tech stack

- Python 3.11+
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) (`mcp[cli]`)
- `httpx` for async HTTP
- [uv](https://docs.astral.sh/uv/) for dependency and environment management
- National Weather Service REST API (GeoJSON)

## Project structure

```
mcp_demo/
├── Server/
│   └── weather.py      # The MCP server and the get_alerts tool
├── pyproject.toml      # Project metadata and dependencies
└── uv.lock             # Locked dependency versions
```

## Getting started

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 22.19+ (only needed for the MCP Inspector)

### Install

```bash
git clone https://github.com/rakshithajagadeesh11-cmd/mcp_demo.git
cd mcp_demo
uv sync
```

### Test with the MCP Inspector

```bash
uv run mcp dev Server/weather.py
```

This opens a browser tab. Click **Connect**, open the **Tools** tab, choose `get_alerts`, enter a state code such as `CA`, and click **Run Tool**.

### Use with Claude Code

```bash
claude mcp add weather -- uv --directory /absolute/path/to/mcp_demo run Server/weather.py
```

### Use with Claude Desktop

```bash
uv run mcp install Server/weather.py
```

Restart Claude Desktop and ask about weather alerts in any US state.

## Example output

```
Event: Air Quality Alert
Area: Imperial County Southwest; Imperial County Southeast; Imperial Valley
Severity: Unknown
Description: The Imperial County APCD has updated an air quality alert due to
harmful levels of particle pollution from windblown dust...
Instructions: ...
```

## How it works

1. An MCP client (e.g. Claude) calls the `get_alerts` tool with a state code.
2. The server sends a request to `https://api.weather.gov/alerts/active/area/{state}`.
3. It formats each alert in the response into readable text.
4. The formatted alerts go back to the client, which uses them to answer the user.
