package com.aisupport.service;

import com.aisupport.dto.AIAgentDtos.*;
import com.aisupport.exception.AIAgentException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

import java.util.UUID;

@Service
public class AIAgentClient {
    private final RestTemplate restTemplate;
    private final String baseUrl;
    private final String apiKey;
    public AIAgentClient(RestTemplate restTemplate,
                         @Value("${ai.agent.url:http://python-agent:8001}") String baseUrl,
                         @Value("${security.ai-agent-api-key:}") String apiKey) {
        this.restTemplate=restTemplate; this.baseUrl=baseUrl; this.apiKey=apiKey;
    }

    @Retryable(retryFor = RestClientException.class, maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2))
    public Response invoke(Request request) {
        try {
            var headers=new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("X-Request-ID", UUID.randomUUID().toString());
            if (apiKey != null && !apiKey.isBlank()) headers.set("X-AI-Agent-Key", apiKey);
            var response=restTemplate.exchange(baseUrl+"/api/invoke", HttpMethod.POST,
                new HttpEntity<>(request,headers), Response.class);
            if (response.getBody()==null) throw new AIAgentException("Empty AI response", null);
            return response.getBody();
        } catch (RestClientException e) {
            throw e;
        }
    }

    @org.springframework.retry.annotation.Recover
    public Response recover(RestClientException e, Request request) {
        throw new AIAgentException("Failed to call AI agent after retries", e);
    }
}
