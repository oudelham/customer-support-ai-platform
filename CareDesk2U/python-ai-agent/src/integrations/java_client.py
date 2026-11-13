from typing import Any
import httpx

from src.config import get_settings


class JavaBackendClient:
    """Thin client for the existing Spring Boot REST API."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.settings.java_api_key:
            headers["X-Internal-API-Key"] = self.settings.java_api_key
        return headers

    async def _request(
        self, method: str, path: str, *, params: dict[str, Any] | None = None,
        json: Any = None
    ) -> Any:
        url = f"{self.settings.java_backend_url.rstrip('/')}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method, url, headers=self._headers(), params=params, json=json
            )
            response.raise_for_status()
            if not response.content:
                return {"success": True}
            return response.json()

    async def get_customer(self, customer_id: str) -> Any:
        return await self._request("GET", f"/api/v1/customers/{customer_id}")

    async def update_customer(self, customer_id: str, data: dict[str, Any]) -> Any:
        return await self._request("PUT", f"/api/v1/customers/{customer_id}", json=data)

    async def list_customers(self, filter_text: str = "") -> Any:
        return await self._request(
            "GET", "/api/v1/customers", params={"search": filter_text}
        )

    async def create_ticket(self, data: dict[str, Any]) -> Any:
        return await self._request("POST", "/api/v1/tickets", json=data)

    async def get_ticket(self, ticket_id: str) -> Any:
        return await self._request("GET", f"/api/v1/tickets/{ticket_id}")

    async def update_ticket(self, ticket_id: str, status: str, priority: str) -> Any:
        return await self._request(
            "PUT", f"/api/v1/tickets/{ticket_id}",
            json={"status": status, "priority": priority},
        )

    async def search_tickets(self, query: str, customer_id: str = "") -> Any:
        result = await self._request(
            "GET", "/api/v1/tickets",
            params={"search": query, **({"customer_id": customer_id} if customer_id else {})},
        )
        return result.get("data", []) if isinstance(result, dict) else result

    async def add_comment(self, ticket_id: str, message: str) -> Any:
        return await self._request(
            "POST", f"/api/v1/tickets/{ticket_id}/comments",
            json={"text": message},
        )

    async def get_invoices(self, customer_id: str) -> Any:
        result = await self._request(
            "GET", f"/api/v1/customers/{customer_id}/invoices"
        )
        return result.get("data", []) if isinstance(result, dict) else result

    async def get_invoice(self, invoice_id: str) -> Any:
        return await self._request("GET", f"/api/v1/invoices/{invoice_id}")

    async def get_account_status(self, customer_id: str) -> Any:
        return await self._request("GET", f"/api/v1/customers/{customer_id}/status")

    async def verify_customer(self, email: str) -> Any:
        customers = await self.list_customers(email)
        items = customers if isinstance(customers, list) else customers.get("content", [])
        match = next((c for c in items if c.get("email") == email), None)
        return {
            "exists": match is not None,
            "id": match.get("id") if match else None,
            "status": match.get("status") if match else None,
        }
