package com.aisupport;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.retry.annotation.EnableRetry;
import io.github.cdimascio.dotenv.Dotenv;

@SpringBootApplication
@EnableRetry
public class Application {
    public static void main(String[] args) {
        Dotenv dotenv = Dotenv.configure()
            .directory("./")
            .ignoreIfMissing()
            .load();

        dotenv.entries().forEach(entry ->
                System.setProperty(entry.getKey(), entry.getValue())
        );

        SpringApplication.run(Application.class, args);
    }
}