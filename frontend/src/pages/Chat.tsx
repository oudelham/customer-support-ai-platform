import React, { useEffect, useRef, useState } from "react";
import { useAuthStore } from "../store/authStore";
import { useChatStore } from "../store/chatStore";
import { chatService } from "../services/chatService";

export const Chat: React.FC = () => {
  const user = useAuthStore(s => s.user);
  const { messages, sessionId, setSessionId, addMessage, isLoading, setIsLoading } = useChatStore();
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sessionId) 
      setSessionId(chatService.createChatSession());
  }, [sessionId, setSessionId]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !sessionId || isLoading) 
      return;
    const text = input.trim();
    setInput("");
    addMessage({
      id: `user-${Date.now()}`, author: "user", text, timestamp: new Date().toISOString()
    });
    setIsLoading(true);
    try {
      const response = await chatService.sendMessage({ message: text, sessionId });
      addMessage({
        id: response.id,
        author: "ai",
        text: response.response,
        timestamp: response.timestamp,
        suggestedActions: response.suggestedActions,
        ticketCreated: response.ticketCreated,
        ticket: response.ticket
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="chat card">
      <div className="card-header">
        <div><h2>Support Chat</h2><p className="muted">Hello {user?.name}, how can we help?</p></div>
        <span className="pill">{user?.role}</span>
      </div>
      <div className="messages">
        {messages.length === 0 && <div className="empty">Start a conversation with the AI assistant.</div>}
        {messages.map(m => (
          <div key={m.id} className={`message ${m.author}`}>
            <div className="bubble">
              <div>{m.text}</div>
              {m.ticketCreated && m.ticket && (
                <div className="ticket-note">Ticket #{m.ticket.number} · {m.ticket.status}</div>
              )}
              {m.suggestedActions?.length ? (
                <div className="actions">{m.suggestedActions.map(a => <span key={a} className="action">{a}</span>)}</div>
              ) : null}
            </div>
            <small>{new Date(m.timestamp).toLocaleTimeString()}</small>
          </div>
        ))}
        {isLoading && <div className="message ai"><div className="bubble">Thinking…</div></div>}
        <div ref={endRef} />
      </div>
      <form className="chat-form" onSubmit={send}>
        <textarea value={input} onChange={e => setInput(e.target.value)} placeholder="Describe your issue..." rows={3} disabled={isLoading} />
        <button className="primary" disabled={!input.trim() || isLoading}>Send</button>
      </form>
    </section>
  );
};