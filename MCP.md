{
  "mcpServers": {
    "server-sequential-thinking": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "@smithery/cli@latest",
        "run",
        "@smithery-ai/server-sequential-thinking",
        "--key",
        "far-angelfish-LeI7K9"
      ]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@monotool/context7-mcp@latest"]
    },
    "playwright-mcp": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "filesystem": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "d:\\Bll_tests\\"
      ]
    },
    "wcgw": {
      "command": "npx",
      "args": ["-y", "@somepackage/wcgw-mcp@latest"]
    },
    "firecrawl-mcp": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "fc-400deb1479d14861bcd4115e7776b14f"
      }
    }
  }
}
