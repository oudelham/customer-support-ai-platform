package com.aisupport.security;

import com.aisupport.repository.UserRepository;
import org.springframework.security.core.userdetails.*;
import org.springframework.stereotype.Service;

@Service
public class CustomUserDetailsService implements UserDetailsService {
    private final UserRepository users;
    public CustomUserDetailsService(UserRepository users) { this.users = users; }
    @Override public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        var u = users.findByEmail(email).orElseThrow(() -> new UsernameNotFoundException(email));
        return User.withUsername(u.getEmail()).password(u.getPasswordHash())
            .roles(u.getRole().toUpperCase()).disabled(!u.isEnabled()).build();
    }
}
