package com.aisupport.dto;
import java.time.LocalDateTime;
import java.util.List;
public record ChatResponse(
    String id, String response, List<String> suggestedActions,
    boolean ticketCreated, TicketSummary ticket, LocalDateTime timestamp
) {}
