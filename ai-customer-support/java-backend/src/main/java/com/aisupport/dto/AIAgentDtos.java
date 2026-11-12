package com.aisupport.dto;

import java.util.List;
import java.util.Map;

public final class AIAgentDtos {
    private AIAgentDtos() {}
    public record ConversationMessage(String role, String content) {}
    public record Request(String message, String customerId, String customerEmail, String customerTier,
                          String sessionId, List<ConversationMessage> conversationHistory, Map<String,Object> context) {}
    public record TicketData(String title, String description, String category, String priority) {}
    public record Response(String response, List<String> suggestedActions, boolean ticketCreated,
                           TicketData ticketData, double confidence, List<String> sources) {}
}
