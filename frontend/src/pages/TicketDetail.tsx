import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ticketService } from "../services/ticketService";
import { Ticket } from "../types";

export const TicketDetail: React.FC = () => {
  const { ticketId } = useParams();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [comment, setComment] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (ticketId) ticketService.getTicket(Number(ticketId)).then(setTicket).catch(() => setMessage("Unable to load ticket."));
  }, [ticketId]);

  const addComment = async () => {
    if (!ticket || !comment.trim()) return;
    await ticketService.addComment(ticket.id, comment.trim());
    setComment("");
    setMessage("Comment submitted.");
  };

  if (!ticket) return <div className="card">{message || "Loading…"}</div>;

  return (
    <section className="card">
      <h2>Ticket #{ticket.number}</h2>
      <p className="muted">{ticket.title}</p>
      <div className="grid2">
        <div><strong>Status</strong><p>{ticket.status}</p></div>
        <div><strong>Priority</strong><p>{ticket.priority}</p></div>
        <div><strong>Category</strong><p>{ticket.category}</p></div>
        <div><strong>Created by</strong><p>{ticket.createdBy}</p></div>
      </div>
      <hr />
      <p>{ticket.description}</p>
      {ticket.aiConfidence != null && <p><strong>AI confidence:</strong> {Math.round(ticket.aiConfidence * 100)}%</p>}
      <h3>Add comment</h3>
      <textarea value={comment} onChange={e => setComment(e.target.value)} rows={3} />
      <button className="primary" onClick={() => void addComment()}>Submit</button>
      {message && <p className="muted">{message}</p>}
    </section>
  );
};