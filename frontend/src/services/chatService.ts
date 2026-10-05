import { apiClient } from "./api";
import { ChatRequest, ChatResponse } from "../types";

export const chatService = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>("/chat", request);
    return response.data;
  },

  async getChatHistory(sessionId: string) {
    const response = await apiClient.get<{
      session_id: string;
      messages: unknown[];
    }>(`/chat/history/${encodeURIComponent(sessionId)}`);
    return response.data;
  },

  createChatSession(): string {
    return `sess_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;
  }
};