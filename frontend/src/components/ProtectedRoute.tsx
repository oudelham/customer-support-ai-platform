import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

export const ProtectedRoute: React.FC = () => {
  const authenticated = useAuthStore((state) => state.isAuthenticated());
  return authenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export const OfficerRoute: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  if (!user) return <Navigate to="/login" replace />;
  return user.role === "officer" || user.role === "admin"
    ? <Outlet />
    : <Navigate to="/chat" replace />;
};