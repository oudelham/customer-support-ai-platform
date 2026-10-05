package com.aisupport.service;

import com.aisupport.dto.AuthDtos.*;
import com.aisupport.entity.User;
import com.aisupport.repository.UserRepository;
import com.aisupport.security.JwtTokenProvider;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {
    private final UserRepository users;
    private final PasswordEncoder encoder;
    private final JwtTokenProvider tokens;

    public AuthService(UserRepository users, PasswordEncoder encoder, JwtTokenProvider tokens) {
        this.users=users; this.encoder=encoder; this.tokens=tokens;
    }

    public LoginResponse login(LoginRequest request) {
        User u = users.findByEmail(request.email()).orElseThrow(() -> new IllegalArgumentException("Invalid credentials"));
        //Test 
        String rawPassword = request.password();
        String hashFromDb = u.getPasswordHash();

        System.out.println("Raw password     : [" + rawPassword + "]");
        System.out.println("Hash from DB     : [" + hashFromDb + "]");
        System.out.println("Matches result   : " + encoder.matches(rawPassword, hashFromDb));
        System.out.println("Encoder class    : " + encoder.getClass().getName());

        String testHash = encoder.encode("password");
        System.out.println("Newly generated hash: " + testHash);
        System.out.println("Matches new hash?    : " + encoder.matches("password", testHash));

        if (!u.isEnabled() || !encoder.matches(request.password(), u.getPasswordHash()))
            throw new IllegalArgumentException("Invalid credentials");

        return new LoginResponse(tokens.createAccessToken(u.getId(),u.getEmail(),u.getRole()),
            tokens.createRefreshToken(u.getId(),u.getEmail(),u.getRole()),
            new UserView(u.getId(),u.getEmail(),u.getName(),u.getRole()));
    }
    
    public AccessResponse refresh(RefreshRequest request) {
        var claims = tokens.parse(request.refreshToken());
        if (!"refresh".equals(claims.get("type", String.class))) throw new IllegalArgumentException("Invalid refresh token");
        return new AccessResponse(tokens.createAccessToken(Long.valueOf(claims.getSubject()),
            claims.get("email", String.class), claims.get("role", String.class)));
    }
}
