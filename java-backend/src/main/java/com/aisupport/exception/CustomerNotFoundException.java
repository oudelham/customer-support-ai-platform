package com.aisupport.exception;
public class CustomerNotFoundException extends RuntimeException {
    public CustomerNotFoundException(Long id) { super("Customer not found: " + id); }
}
