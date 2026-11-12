package com.aisupport.dto;
public final class AuthDtos {
    private AuthDtos() {}
    public record LoginRequest(String email, String password) {}
    public record RefreshRequest(String refreshToken) {}
    public record LoginResponse(String accessToken, String refreshToken, UserView user) {}
    public record AccessResponse(String accessToken) {}
    public record UserView(Long id, String email, String name, String role) {}
}
