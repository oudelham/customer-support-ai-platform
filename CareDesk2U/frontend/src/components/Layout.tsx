import React from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

export const Layout: React.FC = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const doLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <strong>Customer Support AI</strong>
          <span className="muted"> · {user?.name}</span>
        </div>
        <nav>
          {(user?.role === "customer") && (
            <Link to="/chat">Chat</Link>
          )}
          <Link to="/tickets">Tickets</Link>
          {(user?.role === "officer" || user?.role === "admin") && (
            <Link to="/officer/ai-review">AI Review</Link>
          )}
          <button onClick={doLogout}>Logout</button>
        </nav>
      </header>
      <main className="content"><Outlet /></main>
    </div>
  );
};