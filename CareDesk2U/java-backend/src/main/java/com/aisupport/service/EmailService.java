package com.aisupport.service;

import com.aisupport.entity.Ticket;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service @Slf4j
public class EmailService {
    public void sendTicketCreatedEmail(Ticket ticket) {
        log.info("Email notification requested for ticket {}",ticket.getTicketNumber());
        // SMTP/SES integration can be plugged in here without changing TicketService.
    }
}
