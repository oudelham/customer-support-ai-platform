import React, { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

export const Login: React.FC = () => {
  const { user, login, isLoading, error } = useAuthStore();
  const navigate = useNavigate();
  const [email, setEmail] = useState("john@aisupport.com");
  const [password, setPassword] = useState("password");

  if (user?.role === 'customer') return <Navigate to="/chat" replace />;
  if (user?.role === 'officer') return <Navigate to="/tickets" replace />;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email, password);
    if (user?.role === 'customer') navigate("/chat");
    if (user?.role === 'officer') navigate("/tickets");
  };

  return (
    <div className="login-page">
      <form className="card login-card" onSubmit={submit}>
        <h1>Customer Support AI</h1>
        <p className="muted">Sign in.</p>
        <label>Email<input value={email} onChange={e => setEmail(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} /></label>
        {error && <div className="error">{error}</div>}
        <button className="primary" disabled={isLoading}>{isLoading ? "Signing in..." : "Sign in"}</button>
      </form>
    </div>
  );
};