package com.aisupport.exception;

import com.aisupport.dto.ErrorResponse;
import org.springframework.http.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(CustomerNotFoundException.class)
    ResponseEntity<ErrorResponse> customer(CustomerNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new ErrorResponse(e.getMessage(), "CUSTOMER_NOT_FOUND", java.time.Instant.now()));
    }
    @ExceptionHandler(TicketNotFoundException.class)
    ResponseEntity<ErrorResponse> ticket(TicketNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new ErrorResponse(e.getMessage(), "TICKET_NOT_FOUND", java.time.Instant.now()));
    }
    @ExceptionHandler(com.aisupport.exception.AIAgentException.class)
    ResponseEntity<ErrorResponse> ai(AIAgentException e) {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(new ErrorResponse("AI service temporarily unavailable", "AI_UNAVAILABLE", java.time.Instant.now()));
    }
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<ErrorResponse> validation(MethodArgumentNotValidException e) {
        return ResponseEntity.badRequest().body(new ErrorResponse("Invalid request", "VALIDATION_ERROR", java.time.Instant.now()));
    }
}
