package com.aisupport.service;

import com.aisupport.dto.*;
import com.aisupport.dto.AIAgentDtos.*;
import com.aisupport.entity.ChatMessage;
import com.aisupport.repository.ChatMessageRepository;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;

@Service
public class ChatService {
    private final AIAgentClient ai;
    private final CustomerService customers;
    private final TicketService tickets;
    private final ChatMessageRepository messages;
    private final RedisTemplate<String,Object> redis;

    public ChatService(AIAgentClient ai, CustomerService customers, TicketService tickets,
                       ChatMessageRepository messages, RedisTemplate<String,Object> redis) {
        this.ai=ai; this.customers=customers; this.tickets=tickets; this.messages=messages; this.redis=redis;
    }

    @Transactional
    public ChatResponse handleMessage(Long customerId, String message, String sessionId) {
        var customer=customers.getCustomer(customerId);
        var history=getHistory(sessionId);
        var conversation = history.stream()
            .map(m -> new ConversationMessage("ai".equalsIgnoreCase(m.getAuthor()) ? "assistant" : "user", m.getMessage()))
            .toList();
        var request=new Request(message,String.valueOf(customerId),customer.getEmail(),customer.getTier(),
            sessionId,conversation,Map.of());
        var response=ai.invoke(request);

        TicketSummary summary=null;
        if (response.ticketCreated() && response.ticketData()!=null) {
            var ticket=tickets.createFromAI(customerId,response.ticketData(),response.confidence());
            summary=new TicketSummary(ticket.getId(),ticket.getTicketNumber(),ticket.getStatus(),ticket.getAiConfidence());
        }

        var userMsg=saveMessage(customerId,sessionId,"user",message);
        var aiMsg=saveMessage(customerId,sessionId,"ai",response.response());
        updateCache(sessionId,userMsg,aiMsg);

        return new ChatResponse(String.valueOf(aiMsg.getId()),response.response(),
            response.suggestedActions(),response.ticketCreated(),summary,LocalDateTime.now());
    }

    private ChatMessage saveMessage(Long customerId,String sessionId,String author,String text) {
        var m=new ChatMessage();
        m.setCustomerId(customerId); m.setSessionId(sessionId); m.setAuthor(author);
        m.setMessage(text); m.setCreatedAt(LocalDateTime.now());
        return messages.save(m);
    }

    @SuppressWarnings("unchecked")
    public List<ChatMessage> getHistory(String sessionId) {
        String key="chat:"+sessionId+":history";
        var cached=redis.opsForList().range(key,0,-1);
        if (cached!=null && !cached.isEmpty()) {
            return cached.stream().filter(ChatMessage.class::isInstance).map(x -> (ChatMessage)x).toList();
        }
        var history=messages.findBySessionIdOrderByCreatedAtAsc(sessionId);
        if (!history.isEmpty()) redis.opsForList().rightPushAll(key,new ArrayList<>(history));
        redis.expire(key,Duration.ofHours(24));
        return history;
    }

    private void updateCache(String sessionId,ChatMessage user,ChatMessage aiMsg) {
        String key="chat:"+sessionId+":history";
        redis.opsForList().rightPush(key,user);
        redis.opsForList().rightPush(key,aiMsg);
        Long size=redis.opsForList().size(key);
        if (size!=null && size>50) redis.opsForList().trim(key,size-50,size-1);
        redis.expire(key,Duration.ofHours(24));
    }
}
