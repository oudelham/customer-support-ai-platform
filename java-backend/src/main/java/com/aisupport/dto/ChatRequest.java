package com.aisupport.dto;
import jakarta.validation.constraints.*;
public record ChatRequest(
    @NotBlank @Size(max=5000) String message,
    @NotBlank @Size(max=100) String sessionId
) {}
