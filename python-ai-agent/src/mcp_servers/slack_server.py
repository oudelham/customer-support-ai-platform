from __future__ import annotations

import httpx
from mcp.server import MCPServer
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.config import get_settings

mcp = MCPServer("slack-integration")


def headers() -> dict[str, str]:
    settings = get_settings()
    return {"Authorization": f"Bearer {settings.slack_bot_token}"}


async def slack(method: str, payload: dict | None = None):
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"https://slack.com/api/{method}",
            headers=headers(),
            json=payload or {},
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("error", "Slack API error"))
        return data


@mcp.tool()
async def send_message(channel: str, message: str) -> dict:
    """Send a Slack message to a channel."""
    return await slack("chat.postMessage", {"channel": channel, "text": message})


@mcp.tool()
async def create_thread(channel: str, thread_ts: str, message: str) -> dict:
    """Reply in an existing Slack thread."""
    return await slack("chat.postMessage", {
        "channel": channel, "thread_ts": thread_ts, "text": message
    })


@mcp.tool()
async def notify_team(message: str, channels: list[str]) -> list:
    """Send the same notification to multiple Slack channels."""
    return [await send_message(channel, message) for channel in channels]


@mcp.tool()
async def update_status(user_id: str, status: str) -> dict:
    """Set a Slack profile status."""
    return await slack("users.profile.set", {
        "profile": {"status_text": status, "status_emoji": ":robot_face:"}
    })


@mcp.tool()
async def list_channels() -> list:
    """List channels visible to the bot."""
    data = await slack("conversations.list", {"limit": 200})
    return data.get("channels", [])


@mcp.tool()
async def get_channel_info(channel: str) -> dict:
    """Get metadata for a Slack channel."""
    return await slack("conversations.info", {"channel": channel})


@mcp.tool()
async def add_reaction(message_ts: str, emoji: str, channel: str) -> dict:
    """Add a reaction to a Slack message."""
    return await slack("reactions.add", {
        "channel": channel, "timestamp": message_ts, "name": emoji
    })


@mcp.custom_route("/tools/send_message", methods=["POST"])
async def send_message_compat(request: Request) -> Response:
    """Internal REST compatibility endpoint for the Java approval workflow.

    The AI agent itself uses MCP at /mcp. Java uses this small internal adapter
    so the existing approval service can notify Slack without embedding an MCP
    client dependency in the Spring Boot application.
    """
    settings = get_settings()
    expected = settings.internal_api_key
    supplied = request.headers.get("X-Internal-API-Key")
    if expected and supplied != expected:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    payload = await request.json()
    channel = payload.get("channel")
    text = payload.get("text")
    if not channel or not text:
        return JSONResponse({"error": "channel and text are required"}, status_code=400)
    try:
        result = await slack("chat.postMessage", {"channel": channel, "text": text})
        return JSONResponse(result)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=502)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8103)
