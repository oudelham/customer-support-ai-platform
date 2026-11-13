import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { OfficerRoute, ProtectedRoute } from "./components/ProtectedRoute";
import { Login } from "./pages/Login";
import { Chat } from "./pages/Chat";
import { Tickets } from "./pages/Tickets";
import { TicketDetail } from "./pages/TicketDetail";
import { AITicketReview } from "./pages/AITicketReview";
import "./styles.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/chat" element={<Chat />} />
            <Route path="/tickets" element={<Tickets />} />
            <Route path="/tickets/:ticketId" element={<TicketDetail />} />
            <Route element={<OfficerRoute />}>
              <Route path="/officer/ai-review" element={<AITicketReview />} />
            </Route>
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </BrowserRouter>
  );
}