package com.aisupport.controller;

import com.aisupport.dto.AuthDtos.*;
import com.aisupport.service.AuthService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/v1/auth")
public class AuthController {
    private final AuthService auth;
    public AuthController(AuthService auth){this.auth=auth;}
    @PostMapping("/login") public ResponseEntity<LoginResponse> login(@RequestBody LoginRequest req){return ResponseEntity.ok(auth.login(req));}
    @PostMapping("/refresh") public ResponseEntity<AccessResponse> refresh(@RequestBody RefreshRequest req){return ResponseEntity.ok(auth.refresh(req));}
    @PostMapping("/logout") public ResponseEntity<?> logout(){return ResponseEntity.ok(java.util.Map.of("message","Logged out successfully"));}
}
