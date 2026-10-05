package com.aisupport.repository;
import com.aisupport.entity.Customer;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
public interface CustomerRepository extends JpaRepository<Customer, Long> {
    Optional<Customer> findByEmail(String email);
    java.util.List<Customer> findByNameContainingIgnoreCaseOrEmailContainingIgnoreCase(String name,String email);
}
