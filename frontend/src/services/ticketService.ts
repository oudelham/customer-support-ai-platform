import { apiClient } from "./api";
import {
  ApprovalRequest,
  AITicketReview,
  PaginatedResponse,
  Ticket
} from "../types";

export const ticketService = {
  async listTickets(
    page = 0,
    pageSize = 10,
    status?: string,
    priority?: string,
    search?: string
  ): Promise<PaginatedResponse<Ticket>> {
    const params = new URLSearchParams({
      page: page.toString(),
      pageSize: pageSize.toString()
    });
    if (status) params.set("status", status);
    if (priority) params.set("priority", priority);
    if (search) params.set("search", search);

    const response = await apiClient.get<PaginatedResponse<Ticket>>(
      `/tickets?${params.toString()}`
    );
    return {
      ...response.data,
      data: response.data.data.map((ticket) => ({
        ...ticket,
        number: ticket.number || ticket.ticketNumber || String(ticket.id),
      })),
    };
  },

  async getTicket(ticketId: number): Promise<Ticket> {
    const response = await apiClient.get<Ticket>(`/tickets/${ticketId}`);
    const ticket = response.data;
    return { ...ticket, number: ticket.number || ticket.ticketNumber || String(ticket.id) };
  },

  async createTicket(data: {
    title: string;
    description: string;
    priority: string;
    category: string;
  }): Promise<Ticket> {
    const response = await apiClient.post<Ticket>("/tickets", data);
    return response.data;
  },

  async updateTicket(ticketId: number, data: Partial<Ticket>): Promise<Ticket> {
    const response = await apiClient.put<Ticket>(`/tickets/${ticketId}`, data);
    return response.data;
  },

  async addComment(ticketId: number, text: string) {
    const response = await apiClient.post(`/tickets/${ticketId}/comments`, { text });
    return response.data;
  },

  async getPendingAITickets(): Promise<{ data: AITicketReview[]; total_pending: number }> {
    const response = await apiClient.get<{ data: AITicketReview[]; total_pending: number }>("/tickets/pending/ai");
    return {
      ...response.data,
      data: response.data.data.map((ticket) => ({
        ...ticket,
        number: ticket.number || ticket.ticketNumber || String(ticket.id),
      })),
    };
  },

  async approveTicket(ticketId: number, data: ApprovalRequest = {}) {
    const response = await apiClient.post(`/tickets/${ticketId}/approve`, data);
    return response.data;
  },

  async rejectTicket(ticketId: number, reason: string) {
    const response = await apiClient.post(`/tickets/${ticketId}/reject`, {
      reason,
      sendNotification: false
    });
    return response.data;
  }
};