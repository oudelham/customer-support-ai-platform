package com.aisupport.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;

@Entity @Table(name="invoices")
@Getter @Setter @NoArgsConstructor
public class Invoice {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name="customer_id", nullable=false) private Long customerId;
    @Column(nullable=false, precision=10, scale=2) private BigDecimal amount;
    @Column(nullable=false) private String status;
    @Column(name="issued_at", nullable=false) private LocalDate issuedAt;
    @Column(name="due_at", nullable=false) private LocalDate dueAt;
    @Column(name="paid_at") private LocalDate paidAt;
}
