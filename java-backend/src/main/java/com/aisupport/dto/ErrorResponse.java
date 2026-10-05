package com.aisupport.dto;
import java.time.Instant;
public record ErrorResponse(String message, String code, Instant timestamp) {
    public ErrorResponse(String message) { this(message, "ERROR", Instant.now()); }
}
