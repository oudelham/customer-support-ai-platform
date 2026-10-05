package com.aisupport.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity @Table(name="users")
@Getter @Setter @NoArgsConstructor
public class User {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable=false, unique=true) private String email;
    @Column(nullable=false) private String name;
    @Column(nullable=false) private String passwordHash;
    @Column(nullable=false) private String role;
    @Column(nullable=false) private boolean enabled = true;
    @Column(name="created_at", nullable=false) private LocalDateTime createdAt;
}
