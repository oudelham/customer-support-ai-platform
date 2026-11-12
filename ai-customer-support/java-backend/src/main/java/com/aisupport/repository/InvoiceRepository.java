package com.aisupport.repository;
import com.aisupport.entity.Invoice;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface InvoiceRepository extends JpaRepository<Invoice, Long> {
    List<Invoice> findByCustomerIdOrderByIssuedAtDesc(Long customerId);
}
