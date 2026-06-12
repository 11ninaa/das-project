package com.example.demo.controller;

import com.example.demo.services.ETLService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/etl")
@CrossOrigin(origins = "https://clientdas15.z36.web.core.windows.net")
public class ETLController {

    @Autowired
    private ETLService etlService;

    /**
     * Manually trigger the ETL pipeline to update crypto data.
     */
    @PostMapping("/trigger")
    public ResponseEntity<Map<String, Object>> triggerETL() {
        try {
            Map<String, Object> result = etlService.triggerETLPipeline();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Get status of the data ingestion service.
     */
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getETLStatus() {
        try {
            return ResponseEntity.ok(Map.of("status", "available", "message", "ETL service is running"));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", e.getMessage()));
        }
    }
}

