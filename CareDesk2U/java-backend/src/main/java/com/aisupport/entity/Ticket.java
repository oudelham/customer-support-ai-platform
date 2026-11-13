package com.aisupport.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity @Table(name="tickets")
@Getter @Setter @NoArgsConstructor
public class Ticket {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name="ticket_number", nullable=false, unique=true) private String ticketNumber;
    @Column(name="customer_id", nullable=false) private Long customerId;
    @Column(nullable=false) private String title;
    @Column(nullable=false, columnDefinition="text") private String description;
    @Column(nullable=false) private String status;
    @Column(nullable=false) private String priority;
    @Column(nullable=false) private String category;
    @Column(name="created_by", nullable=false) private String createdBy;
    @Column(name="ai_confidence") private Double aiConfidence;
    @Column(name="approved_by") private Long approvedBy;
    @Column(name="approved_at") private LocalDateTime approvedAt;
    @Column(name="created_at", nullable=false) private LocalDateTime createdAt;
    @Column(name="resolved_at") private LocalDateTime resolvedAt;
}
