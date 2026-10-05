package com.aisupport.service;

import com.aisupport.entity.Customer;
import com.aisupport.exception.CustomerNotFoundException;
import com.aisupport.repository.CustomerRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CustomerService {
    private final CustomerRepository repo;
    public CustomerService(CustomerRepository repo) { this.repo=repo; }
    public java.util.List<Customer> search(String text) {
        if (text == null || text.isBlank()) return repo.findAll();
        return repo.findByNameContainingIgnoreCaseOrEmailContainingIgnoreCase(text,text);
    }
    public Customer getCustomer(Long id) { return repo.findById(id).orElseThrow(() -> new CustomerNotFoundException(id)); }
    @Transactional public Customer update(Long id, String name, String email) {
        Customer c=getCustomer(id);
        if (name!=null) c.setName(name);
        if (email!=null) c.setEmail(email);
        c.setUpdatedAt(java.time.LocalDateTime.now());
        return repo.save(c);
    }
}
