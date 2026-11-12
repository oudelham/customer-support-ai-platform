package com.aisupport.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
public class InternalApiKeyFilter extends OncePerRequestFilter {
    private final String expected;
    public InternalApiKeyFilter(@Value("${security.internal-api-key:}") String expected) { this.expected = expected; }
    @Override protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain) throws ServletException, IOException {
        String supplied = request.getHeader("X-Internal-API-Key");
        if (expected != null && !expected.isBlank() && expected.equals(supplied)) {
            var auth = new UsernamePasswordAuthenticationToken("internal-ai", null,
                List.of(new SimpleGrantedAuthority("ROLE_AI_SERVICE")));
            org.springframework.security.core.context.SecurityContextHolder.getContext().setAuthentication(auth);
        }
        chain.doFilter(request, response);
    }
}
