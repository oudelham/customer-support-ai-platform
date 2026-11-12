import pytest

from src.mcp_servers.backend_server import mcp


@pytest.mark.asyncio
async def test_mcp_server_has_tools():
    tools = await mcp.list_tools()
    names = {tool.name for tool in tools.tools}
    assert "get_customer" in names
    assert "create_ticket" in names
