package com.aisupport.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "security.jwt")
public record JwtConfig(String secret, long accessExpirationMs, long refreshExpirationMs) {}
