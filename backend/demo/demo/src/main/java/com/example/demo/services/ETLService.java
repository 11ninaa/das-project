package com.example.demo.services;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

@Service
public class ETLService {

    private static final Logger logger = LoggerFactory.getLogger(ETLService.class);

    private final RestTemplate restTemplate;
    
    @Value("${microservices.data-ingestion.url}")
    private String dataIngestionUrl;

    @Autowired
    public ETLService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Map<String, Object> triggerETLPipeline() throws Exception {
        String runId = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        
        logger.info("=".repeat(80));
        logger.info("ETL TRIGGER: Starting ETL pipeline [ID: {}]", runId);
        logger.info("ETL TRIGGER: Time: {}", LocalDateTime.now());
        logger.info("ETL TRIGGER: Service URL: {}", dataIngestionUrl);
        logger.info("=".repeat(80));

        try {
            String url = dataIngestionUrl + "/api/data/update";
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            
            logger.info("ETL TRIGGER: Pipeline started successfully [ID: {}]", runId);
            logger.info("ETL TRIGGER: Response: {}", response);
            logger.info("=".repeat(80));
            
            return response != null ? response : Map.of("status", "started", "message", "ETL pipeline triggered");
        } catch (RestClientException e) {
            logger.error("=".repeat(80));
            logger.error("ETL TRIGGER: Failed to trigger ETL pipeline [ID: {}]", runId, e);
            logger.error("ETL TRIGGER: Service URL: {}", dataIngestionUrl);
            logger.error("=".repeat(80));
            throw new Exception("Failed to trigger ETL pipeline: " + e.getMessage(), e);
        }
    }

    @Scheduled(cron = "0 0 1 * * ?", zone = "UTC")
    public void runDailyETLPipeline() {
        try {
            triggerETLPipeline();
        } catch (Exception e) {
            logger.error("ETL SCHEDULER: Scheduled pipeline run failed", e);
        }
    }
}
