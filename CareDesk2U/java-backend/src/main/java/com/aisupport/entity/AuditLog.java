package com.aisupport.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity @Table(name="audit_logs")
@Getter @Setter @NoArgsConstructor
public class AuditLog {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable=false) private String action;
    @Column(name="actor_id") private Long actorId;
    @Column(name="resource_id") private Long resourceId;
    @Column(columnDefinition="text") private String description;
    @Column(nullable=false) private LocalDateTime timestamp;
    @Column(name="ip_address") private String ipAddress;
}
