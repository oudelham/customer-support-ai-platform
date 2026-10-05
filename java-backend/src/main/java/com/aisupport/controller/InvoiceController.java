package com.aisupport.controller;

import com.aisupport.repository.InvoiceRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
public class InvoiceController {
    private final InvoiceRepository invoices;
    public InvoiceController(InvoiceRepository invoices){this.invoices=invoices;}
    @GetMapping("/api/v1/customers/{customerId}/invoices")
    public ResponseEntity<?> invoices(@PathVariable Long customerId){
        return ResponseEntity.ok(java.util.Map.of("data",invoices.findByCustomerIdOrderByIssuedAtDesc(customerId)));
    }
    @GetMapping("/api/v1/invoices/{invoiceId}")
    public ResponseEntity<?> getInvoice(@PathVariable Long invoiceId){
        return invoices.findById(invoiceId).map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.notFound().build());
    }
}
