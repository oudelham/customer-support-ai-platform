import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ticketService } from "../services/ticketService";
import { Ticket } from "../types";

export const Tickets: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const result = await ticketService.listTickets();
      setTickets(result.data);
    } catch (e: any) {
      setError(e?.response?.data?.message || "Failed to load tickets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  return (
    <section>
      <div className="page-title"><div><h2>Tickets</h2><p className="muted">Manage your tickets.</p></div><button onClick={() => void load()}>Refresh</button></div>
      {error && <div className="error">{error}</div>}
      {loading ? <div className="card">Loading…</div> : (
        <div className="card table-wrap">
          <table><thead><tr><th>Number</th><th>Title</th><th>Status</th><th>Priority</th><th>Category</th><th>AI</th></tr></thead>
          <tbody>
            {tickets.map(t => <tr key={t.id}>
              <td><Link to={`/tickets/${t.id}`}>#{t.number}</Link></td>
              <td>{t.title}</td><td><span className="pill">{t.status}</span></td>
              <td>{t.priority}</td><td>{t.category}</td>
              <td>{t.aiConfidence != null ? `${Math.round(t.aiConfidence * 100)}%` : "—"}</td>
            </tr>)}
            {!tickets.length && <tr><td colSpan={6}>No tickets found.</td></tr>}
          </tbody></table>
        </div>
      )}
    </section>
  );
};