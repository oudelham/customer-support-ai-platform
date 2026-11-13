package com.aisupport.service;

import com.aisupport.dto.AIAgentDtos.TicketData;
import com.aisupport.dto.TicketUpdateRequest;
import com.aisupport.entity.Ticket;
import com.aisupport.exception.TicketNotFoundException;
import com.aisupport.repository.TicketRepository;
import com.aisupport.repository.AuditLogRepository;
import com.aisupport.entity.AuditLog;
import org.springframework.data.domain.*;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.*;
import java.util.*;

@Service
public class TicketService {
    private final TicketRepository repo;
    private final AuditLogRepository audit;
    private final RedisTemplate<String,Object> redis;
    private final SlackMcpClient slack;
    private final EmailService email;

    public TicketService(TicketRepository repo, AuditLogRepository audit, RedisTemplate<String,Object> redis,
                         SlackMcpClient slack, EmailService email) {
        this.repo=repo; this.audit=audit; this.redis=redis; this.slack=slack; this.email=email;
    }

    public Ticket createFromAI(Long customerId, TicketData data, double confidence) {
        var t=new Ticket();
        t.setCustomerId(customerId); t.setTicketNumber(nextNumber());
        t.setTitle(data.title()); t.setDescription(data.description());
        t.setCategory(data.category()); t.setPriority(data.priority());
        t.setStatus("pending"); t.setCreatedBy("ai_agent");
        t.setAiConfidence(confidence); t.setCreatedAt(LocalDateTime.now());
        var saved=repo.save(t);
        redis.opsForZSet().add("tickets:pending-ai",saved.getId().toString(),System.currentTimeMillis());
        redis.expire("tickets:pending-ai",Duration.ofSeconds(30));
        audit("TICKET_CREATED_AI",null,saved.getId(),"AI created ticket: "+saved.getTicketNumber());
        return saved;
    }

    @Transactional
    public Ticket create(Long customerId, String title, String description, String priority, String category) {
        var t=new Ticket();
        t.setCustomerId(customerId); t.setTicketNumber(nextNumber()); t.setTitle(title);
        t.setDescription(description); t.setPriority(priority); t.setCategory(category);
        t.setStatus("open"); t.setCreatedBy("user"); t.setCreatedAt(LocalDateTime.now());
        return repo.save(t);
    }

    public Page<Ticket> list(Long customerId,String status,String priority,int page,int pageSize) { return list(customerId,status,priority,page,pageSize,null); }

    public Page<Ticket> list(Long customerId,String status,String priority,int page,int pageSize,String search) {
        var pageable=PageRequest.of(Math.max(0,page),Math.min(Math.max(pageSize,1),100),Sort.by("createdAt").descending());
        if (customerId!=null && search != null && !search.isBlank()) return repo.findByCustomerIdAndTitleContainingIgnoreCaseOrCustomerIdAndDescriptionContainingIgnoreCase(customerId,search,customerId,search,pageable);
        if (customerId!=null) return repo.findByCustomerId(customerId,pageable);
        if (status!=null && priority!=null) return repo.findByStatusAndPriority(status,priority,pageable);
        if (status!=null) return repo.findByStatus(status,pageable);
        return repo.findAll(pageable);
    }

    public Ticket get(Long id) { return repo.findById(id).orElseThrow(() -> new TicketNotFoundException(id)); }

    @Transactional
    public Ticket update(Long id, TicketUpdateRequest req) {
        var t=get(id);
        if(req.status()!=null) t.setStatus(req.status());
        if(req.priority()!=null) t.setPriority(req.priority());
        if(req.category()!=null) t.setCategory(req.category());
        if(req.title()!=null) t.setTitle(req.title());
        if(req.description()!=null) t.setDescription(req.description());
        if("resolved".equals(t.getStatus())) t.setResolvedAt(LocalDateTime.now());
        return repo.save(t);
    }

    @Transactional
    public void approve(Long id, Long officerId, String notes) {
        var t=get(id);
        t.setStatus("open"); t.setApprovedBy(officerId); t.setApprovedAt(LocalDateTime.now());
        repo.save(t);
        audit("TICKET_APPROVED",officerId,id,"Officer approved "+t.getTicketNumber()+(notes==null?"":": "+notes));
        try { slack.sendMessage("#support","New ticket approved: #"+t.getTicketNumber()+" - "+t.getTitle()); }
        catch(Exception ignored) {}
        try { email.sendTicketCreatedEmail(t); } catch(Exception ignored) {}
        redis.opsForZSet().remove("tickets:pending-ai",id.toString());
    }

    @Transactional
    public void reject(Long id, Long officerId, String reason) {
        var t=get(id); t.setStatus("rejected"); repo.save(t);
        audit("TICKET_REJECTED",officerId,id,"Rejected "+t.getTicketNumber()+": "+reason);
        redis.opsForZSet().remove("tickets:pending-ai",id.toString());
    }

    public List<Ticket> pendingAI() { return repo.findByStatusOrderByCreatedAtAsc("pending"); }

    private String nextNumber() {
        long n=repo.count()+1;
        return String.format("TICKET-%03d",n);
    }

    private void audit(String action,Long actor,Long resource,String desc) {
        var a=new AuditLog(); a.setAction(action); a.setActorId(actor); a.setResourceId(resource);
        a.setDescription(desc); a.setTimestamp(LocalDateTime.now()); audit.save(a);
    }
}
