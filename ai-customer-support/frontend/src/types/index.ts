export type Role = "customer" | "officer" | "admin";
export type Tier = "free" | "pro" | "enterprise";

export interface User {
  id: number;
  email: string;
  name: string;
  role: Role;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken?: string;
  user: User;
}

export interface ChatRequest {
  message: string;
  sessionId: string;
}

export interface TicketSummary {
  id: number;
  number: string;
  status: string;
  aiConfidence?: number;
}

export interface ChatResponse {
  id: string;
  response: string;
  suggestedActions: string[];
  ticketCreated: boolean;
  ticket?: TicketSummary;
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  author: "user" | "ai";
  text: string;
  timestamp: string;
  suggestedActions?: string[];
  ticketCreated?: boolean;
  ticket?: TicketSummary;
}

export interface Ticket {
  id: number;
  ticketNumber?: string;
  number: string;
  customerId: number;
  title: string;
  description: string;
  status: "open" | "in_progress" | "resolved" | "closed" | "pending" | "rejected";
  priority: "low" | "medium" | "high" | "urgent";
  category: "support" | "billing" | "technical";
  createdBy: "ai_agent" | "user" | "officer";
  aiConfidence?: number;
  createdAt: string;
  updatedAt: string;
  resolvedAt?: string;
  approvedBy?: number;
}

export interface Comment {
  id: string;
  author: string;
  text: string;
  timestamp: string;
}

export interface Customer {
  id: number;
  email: string;
  name: string;
  tier: Tier;
  status: "active" | "suspended";
  createdAt: string;
}

export interface Invoice {
  id: number;
  customerId: number;
  amount: number;
  status: "pending" | "paid";
  issuedAt: string;
  dueAt: string;
  paidAt?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    current_page: number;
    total_pages: number;
    total_items: number;
    page_size: number;
  };
}

export interface AITicketReview {
  id: number;
  ticketNumber?: string;
  number?: string;
  customerId: number;
  title: string;
  description: string;
  category: string;
  priority: string;
  status: "pending" | "approved" | "rejected" | string;
  aiConfidence?: number;
  createdAt: string;
  approvedBy?: number;
}

export interface Source {
  type: "faq" | "doc" | "ticket" | "kb" | string;
  title: string;
  relevance: number;
}

export interface ApprovalRequest {
  notes?: string;
}

export interface ErrorResponse {
  message?: string;
  error?: string;
  code?: string;
  details?: Record<string, unknown>;
}