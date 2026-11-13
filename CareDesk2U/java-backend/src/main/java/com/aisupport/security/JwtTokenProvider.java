package com.aisupport.security;

import com.aisupport.config.JwtConfig;
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Component;
import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Component
public class JwtTokenProvider {
    private final JwtConfig config;
    public JwtTokenProvider(JwtConfig config) { this.config = config; }

    private SecretKey key() {
        return Keys.hmacShaKeyFor(config.secret().getBytes(StandardCharsets.UTF_8));
    }

    public String createAccessToken(Long userId, String email, String role) {
        return create(userId, email, role, config.accessExpirationMs(), "access");
    }
    public String createRefreshToken(Long userId, String email, String role) {
        return create(userId, email, role, config.refreshExpirationMs(), "refresh");
    }
    private String create(Long userId, String email, String role, long ttl, String type) {
        var now = new Date();
        return Jwts.builder().subject(String.valueOf(userId)).claim("email", email)
            .claim("role", role).claim("type", type)
            .issuedAt(now).expiration(new Date(now.getTime()+ttl))
            .signWith(key()).compact();
    }
    public Claims parse(String token) {
        return Jwts.parser().verifyWith(key()).build().parseSignedClaims(token).getPayload();
    }
    public Long getUserId(String token) { return Long.valueOf(parse(token).getSubject()); }
    public String getRole(String token) { return parse(token).get("role", String.class); }
}
