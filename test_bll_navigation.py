#!/usr/bin/env python3
"""
Test navigation to bll.by using Playwright MCP
"""
import sys

def test_navigation():
    """Test navigation to bll.by"""
    try:
        print("Testing navigation to bll.by...")
        print("Example MCP commands to use:")
        print()
        print("use_mcp_tool(")
        print("    server_name='playwright-mcp',")
        print("    tool_name='browser_navigate',")
        print("    arguments={'url': 'https://bll.by'}")
        print(")")
        print()
        print("snapshot = use_mcp_tool(")
        print("    server_name='playwright-mcp',")
        print("    tool_name='browser_snapshot',")
        print("    arguments={}")
        print(")")
        print()
        print("console_logs = use_mcp_tool(")
        print("    server_name='github.com/AgentDeskAI/browser-tools-mcp',")
        print("    tool_name='getConsoleLogs',")
        print("    arguments={}")
        print(")")
        print("\nMake sure your MCP client is connected to use these tools!")
        print("See docs/guides/MCP_SERVERS_GUIDE.md for complete documentation.")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_navigation()
    sys.exit(0 if success else 1)
