package com.aisupport.controller;

import com.aisupport.dto.*;
import com.aisupport.service.TicketService;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.http.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/v1/tickets")
public class TicketController {
    private final TicketService service;
    public TicketController(TicketService service){this.service=service;}

    @GetMapping
    public ResponseEntity<?> list(@RequestParam(required=false) String status,@RequestParam(required=false) String priority,@RequestParam(required=false) String search,@RequestParam(required=false) Long customer_id,
                                   @RequestParam(defaultValue="0") int page,@RequestParam(defaultValue="10") int pageSize,
                                   Authentication auth) {
        boolean serviceAccount=auth.getAuthorities().stream().anyMatch(a->a.getAuthority().equals("ROLE_AI_SERVICE"));
        Long userId=serviceAccount?null:Long.valueOf(auth.getName());
        boolean officer=serviceAccount || auth.getAuthorities().stream().anyMatch(a->a.getAuthority().equals("ROLE_OFFICER")||a.getAuthority().equals("ROLE_ADMIN"));
        Page<?> p=service.list(customer_id!=null?customer_id:(officer?null:userId),status,priority,page,pageSize,search);
        return ResponseEntity.ok(java.util.Map.of("data",p.getContent(),"pagination",
            java.util.Map.of("current_page",p.getNumber(),"total_pages",p.getTotalPages(),
                "total_items",p.getTotalElements(),"page_size",p.getSize())));
    }

    @GetMapping("/{ticketId}") public ResponseEntity<?> get(@PathVariable Long ticketId){return ResponseEntity.ok(service.get(ticketId));}

    @PostMapping
    public ResponseEntity<?> create(@Valid @RequestBody TicketCreateRequest req,Authentication auth){
        boolean serviceAccount=auth.getAuthorities().stream().anyMatch(a->a.getAuthority().equals("ROLE_AI_SERVICE"));
        Long customerId=serviceAccount ? req.customerId() : Long.valueOf(auth.getName());
        if (customerId == null) return ResponseEntity.badRequest().body(java.util.Map.of("error","customerId is required for AI service requests"));
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(customerId,req.title(),req.description(),req.priority(),req.category()));
    }

    @PutMapping("/{ticketId}") public ResponseEntity<?> update(@PathVariable Long ticketId,@RequestBody TicketUpdateRequest req){
        return ResponseEntity.ok(service.update(ticketId,req));
    }

    @PostMapping("/{ticketId}/approve")
    public ResponseEntity<?> approve(@PathVariable Long ticketId,@RequestBody(required=false) ApproveTicketRequest req,Authentication auth){
        service.approve(ticketId,Long.valueOf(auth.getName()),req==null?null:req.notes());
        return ResponseEntity.ok(java.util.Map.of("success",true,"message","Ticket approved and team notified via Slack","ticket_id",ticketId));
    }

    @PostMapping("/{ticketId}/reject")
    public ResponseEntity<?> reject(@PathVariable Long ticketId,@RequestBody RejectTicketRequest req,Authentication auth){
        service.reject(ticketId,Long.valueOf(auth.getName()),req.reason());
        return ResponseEntity.ok(java.util.Map.of("success",true,"message","Ticket rejected","ticket_id",ticketId));
    }

    @PostMapping("/{ticketId}/comments")
    public ResponseEntity<?> comment(@PathVariable Long ticketId,@Valid @RequestBody CommentRequest req){
        // A dedicated ticket_comments table can be added in a later migration.
        service.get(ticketId);
        return ResponseEntity.status(HttpStatus.CREATED).body(java.util.Map.of("text",req.text(),"ticket_id",ticketId));
    }

    @GetMapping("/pending/ai")
    public ResponseEntity<?> pending(){
        var data=service.pendingAI();
        return ResponseEntity.ok(java.util.Map.of("data",data,"total_pending",data.size()));
    }
}
