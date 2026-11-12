package com.aisupport.controller;

import com.aisupport.dto.*;
import com.aisupport.service.ChatService;
import jakarta.validation.Valid;
import org.springframework.http.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/v1")
public class ChatController {
    private final ChatService chat;
    public ChatController(ChatService chat){this.chat=chat;}

    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> send(@Valid @RequestBody ChatRequest request, Authentication auth) {
        Long customerId=Long.valueOf(auth.getName());
        return ResponseEntity.ok(chat.handleMessage(customerId,request.message(),request.sessionId()));
    }

    @GetMapping("/chat/history/{sessionId}")
    public ResponseEntity<?> history(@PathVariable String sessionId) {
        var history=chat.getHistory(sessionId);
        return ResponseEntity.ok(java.util.Map.of("session_id",sessionId,"messages",history));
    }
}
