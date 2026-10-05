from src.integrations.java_client import JavaBackendClient
from mcp.server import MCPServer

mcp = MCPServer("enterprise-backend")


@mcp.tool()
async def get_customer(customer_id: str) -> dict:
    """Get a customer profile from the Java backend."""
    return await JavaBackendClient().get_customer(customer_id)


@mcp.tool()
async def update_customer(customer_id: str, data: dict) -> dict:
    """Update a customer profile in the Java backend."""
    return await JavaBackendClient().update_customer(customer_id, data)


@mcp.tool()
async def list_customers(filter: str = "") -> list:
    """Search customers by name, email, or other supported backend fields."""
    result = await JavaBackendClient().list_customers(filter)
    return result if isinstance(result, list) else result.get("content", result)


@mcp.tool()
async def create_ticket(customer_id: str, title: str, description: str, category: str, priority: str) -> dict:
    """Create a support ticket in the Java backend."""
    return await JavaBackendClient().create_ticket({
        "customerId": customer_id,
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
    })


@mcp.tool()
async def get_ticket(ticket_id: str) -> dict:
    """Retrieve a support ticket."""
    return await JavaBackendClient().get_ticket(ticket_id)


@mcp.tool()
async def update_ticket(ticket_id: str, status: str, priority: str) -> dict:
    """Update ticket status and priority."""
    return await JavaBackendClient().update_ticket(ticket_id, status, priority)


@mcp.tool()
async def search_tickets(query: str, customer_id: str = "") -> list:
    """Search tickets, optionally scoped to a customer."""
    result = await JavaBackendClient().search_tickets(query, customer_id)
    return result if isinstance(result, list) else result.get("content", result)


@mcp.tool()
async def add_comment(ticket_id: str, message: str) -> dict:
    """Add a comment to a support ticket."""
    return await JavaBackendClient().add_comment(ticket_id, message)


@mcp.tool()
async def get_invoices(customer_id: str) -> list:
    """Retrieve invoices for a customer."""
    result = await JavaBackendClient().get_invoices(customer_id)
    return result if isinstance(result, list) else result.get("content", result)


@mcp.tool()
async def get_invoice(invoice_id: str) -> dict:
    """Retrieve a single invoice."""
    return await JavaBackendClient().get_invoice(invoice_id)


@mcp.tool()
async def get_account_status(customer_id: str) -> dict:
    """Retrieve account/subscription status."""
    return await JavaBackendClient().get_account_status(customer_id)


@mcp.tool()
async def verify_customer(email: str) -> dict:
    """Verify whether a customer exists by email."""
    return await JavaBackendClient().verify_customer(email)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8101)
