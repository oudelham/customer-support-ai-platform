import React, { useEffect, useState } from "react";
import { ticketService } from "../services/ticketService";
import { AITicketReview as Review } from "../types";

export const AITicketReview: React.FC = () => {
  const [tickets, setTickets] = useState<Review[]>([]);
  const [selected, setSelected] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const result = await ticketService.getPendingAITickets();
      setTickets(result.data);
      setSelected(result.data[0] ?? null);
    } catch {
      setMessage("Failed to load pending AI tickets.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const approve = async () => {
    if (!selected) return;
    await ticketService.approveTicket(selected.id, {});
    setMessage(`Ticket #${selected.number} approved.`);
    await load();
  };

  const reject = async () => {
    if (!selected) return;
    await ticketService.rejectTicket(selected.id, "Rejected by officer");
    setMessage(`Ticket #${selected.number} rejected.`);
    await load();
  };

  if (loading) return <div className="card">Loading AI tickets…</div>;

  return (
    <section>
      <div className="page-title"><div><h2>AI Ticket Review</h2><p className="muted">{tickets.length} pending ticket(s)</p></div><button onClick={() => void load()}>Refresh</button></div>
      {message && <div className="success">{message}</div>}
      <div className="review-grid">
        <div className="card">
          {tickets.map(t => (
            <button key={t.id} className={`review-item ${selected?.id === t.id ? "selected" : ""}`} onClick={() => setSelected(t)}>
              <strong>#{t.number} · {t.title}</strong><span>{t.aiConfidence != null ? `${Math.round(t.aiConfidence * 100)}% confidence` : "AI confidence unavailable"}</span>
            </button>
          ))}
          {!tickets.length && <div className="empty">No pending AI tickets.</div>}
        </div>
        <div className="card">
          {selected ? <>
            <h2>{selected.title}</h2>
            <p>{selected.description}</p>
            <div className="grid2">
              <div><strong>Customer ID</strong><p>{selected.customerId}</p></div>
              <div><strong>Tier</strong><p>{selected.customerTier}</p></div>
              <div><strong>Category</strong><p>{selected.category}</p></div>
              <div><strong>Priority</strong><p>{selected.priority}</p></div>
            </div>
            <h3>AI analysis</h3>
            <p>Confidence: {selected.aiConfidence != null ? `${Math.round(selected.aiConfidence * 100)}%` : "unavailable"}</p>
            <p className="muted">The current Java ticket schema does not persist per-ticket RAG source metadata.</p>
            <div className="button-row">
              <button className="primary" onClick={() => void approve()}>Approve & notify</button>
              <button className="danger" onClick={() => void reject()}>Reject</button>
            </div>
          </> : <div className="empty">Select a ticket.</div>}
        </div>
      </div>
    </section>
  );
};