package com.aisupport.dto;
public record TicketUpdateRequest(String status, String priority, String category, String title, String description) {}
