package com.aisupport.dto;
import jakarta.validation.constraints.*;
public record TicketCreateRequest(
    Long customerId, @NotBlank String title, @NotBlank String description,
    @NotBlank String priority, @NotBlank String category) {}
