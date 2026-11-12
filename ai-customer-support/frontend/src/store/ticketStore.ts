import { create } from "zustand";
import { AITicketReview, Ticket } from "../types";

interface TicketState {
  tickets: Ticket[];
  pendingAITickets: AITicketReview[];
  selectedTicket: Ticket | null;
  selectedAITicket: AITicketReview | null;
  isLoading: boolean;
  error: string | null;
  totalPages: number;
  currentPage: number;
  setTickets: (tickets: Ticket[]) => void;
  setPendingAITickets: (tickets: AITicketReview[]) => void;
  setSelectedTicket: (ticket: Ticket | null) => void;
  setSelectedAITicket: (ticket: AITicketReview | null) => void;
  setIsLoading: (value: boolean) => void;
  setError: (error: string | null) => void;
  setPagination: (page: number, totalPages: number) => void;
}

export const useTicketStore = create<TicketState>((set) => ({
  tickets: [],
  pendingAITickets: [],
  selectedTicket: null,
  selectedAITicket: null,
  isLoading: false,
  error: null,
  totalPages: 0,
  currentPage: 0,
  setTickets: (tickets) => set({ tickets }),
  setPendingAITickets: (pendingAITickets) => set({ pendingAITickets }),
  setSelectedTicket: (selectedTicket) => set({ selectedTicket }),
  setSelectedAITicket: (selectedAITicket) => set({ selectedAITicket }),
  setIsLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setPagination: (currentPage, totalPages) => set({ currentPage, totalPages })
}));