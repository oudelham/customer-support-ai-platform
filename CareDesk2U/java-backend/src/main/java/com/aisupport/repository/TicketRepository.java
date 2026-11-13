package com.aisupport.repository;
import com.aisupport.entity.Ticket;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface TicketRepository extends JpaRepository<Ticket, Long> {
    Page<Ticket> findByCustomerId(Long customerId, Pageable pageable);
    Page<Ticket> findByStatusAndPriority(String status, String priority, Pageable pageable);
    Page<Ticket> findByStatus(String status, Pageable pageable);
    List<Ticket> findByStatusOrderByCreatedAtAsc(String status);
    Page<Ticket> findByCustomerIdAndTitleContainingIgnoreCaseOrCustomerIdAndDescriptionContainingIgnoreCase(Long c1,String title,Long c2,String description,Pageable pageable);
}
