package com.aisupport.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity @Table(name="chat_messages")
@Getter @Setter @NoArgsConstructor
public class ChatMessage {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name="session_id", nullable=false) private String sessionId;
    @Column(name="customer_id", nullable=false) private Long customerId;
    @Column(nullable=false) private String author;
    @Column(nullable=false, columnDefinition="text") private String message;
    @Column(name="created_at", nullable=false) private LocalDateTime createdAt;
    @Column(columnDefinition="jsonb") private String metadata;
}
