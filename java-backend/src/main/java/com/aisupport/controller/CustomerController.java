package com.aisupport.controller;

import com.aisupport.service.CustomerService;
import jakarta.validation.constraints.Email;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/v1/customers")
public class CustomerController {
    private final CustomerService service;
    public CustomerController(CustomerService service){this.service=service;}

    @GetMapping
    public ResponseEntity<?> search(@RequestParam(required=false, defaultValue="") String search){
        return ResponseEntity.ok(service.search(search));
    }

    @GetMapping("/{customerId}/status") public ResponseEntity<?> status(@PathVariable Long customerId){
        var c=service.getCustomer(customerId);
        return ResponseEntity.ok(java.util.Map.of("customerId",c.getId(),"status",c.getStatus(),"tier",c.getTier()));
    }

    @GetMapping("/{customerId}") public ResponseEntity<?> get(@PathVariable Long customerId){return ResponseEntity.ok(service.getCustomer(customerId));}

    public record UpdateCustomerRequest(String name,@Email String email){}
    @PutMapping("/{customerId}") public ResponseEntity<?> update(@PathVariable Long customerId,@RequestBody UpdateCustomerRequest req){
        return ResponseEntity.ok(service.update(customerId,req.name(),req.email()));
    }
}
