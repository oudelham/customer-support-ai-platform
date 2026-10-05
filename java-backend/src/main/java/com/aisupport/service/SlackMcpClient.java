package com.aisupport.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.Map;

@Service
public class SlackMcpClient {
    private final RestTemplate rest;
    private final String url;
    private final String apiKey;
    public SlackMcpClient(RestTemplate rest,
                          @Value("${integrations.slack-mcp-url:http://slack-mcp:8103}") String url,
                          @Value("${security.internal-api-key:}") String apiKey) {
        this.rest=rest; this.url=url; this.apiKey=apiKey;
    }
    public void sendMessage(String channel,String text) {
        var headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        if (apiKey != null && !apiKey.isBlank()) headers.set("X-Internal-API-Key", apiKey);
        rest.postForEntity(url+"/tools/send_message",
            new HttpEntity<>(Map.of("channel",channel,"text",text), headers),Void.class);
    }
}
