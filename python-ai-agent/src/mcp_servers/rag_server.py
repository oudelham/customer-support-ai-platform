from mcp.server import MCPServer

from src.rag.retrieval import Retriever
from src.rag.cache import RetrievalCache

mcp = MCPServer("enterprise-knowledge-base")
retriever = Retriever()
cache = RetrievalCache()


@mcp.tool()
async def search_docs(query: str, top_k: int = 5) -> list:
    """Semantic/hybrid search over the enterprise knowledge base."""
    cached = await cache.get(query, "hybrid", top_k)
    if cached:
        return cached
    results = await retriever.search(query, mode="hybrid", top_k=top_k)
    payload = [r.model_dump() for r in results]
    await cache.set(query, "hybrid", top_k, payload)
    return payload


@mcp.tool()
async def search_faq(category: str) -> list:
    """Search FAQ documents by category."""
    return await search_docs(f"FAQ {category}", 5)


@mcp.tool()
async def find_similar_tickets(ticket_id: str) -> list:
    """Find knowledge-base material related to a ticket identifier."""
    return await search_docs(f"ticket {ticket_id}", 5)


@mcp.tool()
async def hybrid_search(query: str, mode: str = "hybrid") -> list:
    """Search using semantic or hybrid retrieval."""
    results = await retriever.search(query, mode=mode, top_k=5)
    return [r.model_dump() for r in results]


@mcp.tool()
async def get_doc_context(doc_id: str, expand: bool = True) -> dict:
    """Retrieve a specific indexed document chunk by id."""
    result = await retriever.get_context(doc_id)
    return result.model_dump() if result else {"found": False}


@mcp.tool()
async def search_with_metadata(query: str, filters: dict) -> list:
    """Search knowledge base; metadata filters can be added to this interface."""
    results = await retriever.search(query, mode="hybrid", top_k=10)
    filtered = []
    for r in results:
        if all(r.metadata.get(k) == v for k, v in filters.items()):
            filtered.append(r.model_dump())
    return filtered


@mcp.tool()
async def evaluate_retrieval(query: str) -> dict:
    """Return retrieval diagnostics for a query."""
    results = await retriever.search(query, mode="hybrid", top_k=5)
    return {
        "query": query,
        "result_count": len(results),
        "top_score": results[0].score if results else 0.0,
        "context_relevance": sum(r.score for r in results) / len(results) if results else 0.0,
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8102)
