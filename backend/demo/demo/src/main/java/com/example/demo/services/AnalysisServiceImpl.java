/**
 * Analysis service implementation using HTTP calls to microservices.
 */
package com.example.demo.services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Map;

@Service
public class AnalysisServiceImpl implements AnalysisService {

    private final RestTemplate restTemplate;
    
    @Value("${microservices.technical-analysis.url}")
    private String technicalAnalysisUrl;
    
    @Value("${microservices.lstm-prediction.url}")
    private String lstmPredictionUrl;
    
    @Value("${microservices.onchain-sentiment.url}")
    private String onchainSentimentUrl;
    
    @Autowired
    public AnalysisServiceImpl(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    @Override
    public Map<String, Object> getTechnicalAnalysis(String symbol, String timeframe) throws Exception {
        try {
            String url = UriComponentsBuilder
                .fromHttpUrl(technicalAnalysisUrl + "/api/technical/{symbol}")
                .queryParam("timeframe", timeframe)
                .buildAndExpand(symbol)
                .toUriString();
            
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new Exception("Technical analysis service returned empty response");
            }
        } catch (HttpClientErrorException | HttpServerErrorException e) {
            String errorMessage = extractErrorMessage(e.getResponseBodyAsString());
            throw new Exception("Technical analysis failed: " + errorMessage, e);
        } catch (RestClientException e) {
            throw new Exception("Failed to connect to technical analysis service: " + e.getMessage(), e);
        }
    }

    @Override
    public Map<String, Object> getLSTMPrediction(String symbol, int daysAhead) throws Exception {
        try {
            String url = UriComponentsBuilder
                .fromHttpUrl(lstmPredictionUrl + "/api/lstm/{symbol}")
                .queryParam("daysAhead", daysAhead)
                .buildAndExpand(symbol)
                .toUriString();
            
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new Exception("LSTM prediction service returned empty response");
            }
        } catch (HttpClientErrorException | HttpServerErrorException e) {
            String errorMessage = extractErrorMessage(e.getResponseBodyAsString());
            throw new Exception("LSTM prediction failed: " + errorMessage, e);
        } catch (RestClientException e) {
            throw new Exception("Failed to connect to LSTM prediction service: " + e.getMessage(), e);
        }
    }

    @Override
    public Map<String, Object> getOnChainSentiment(String symbol) throws Exception {
        try {
            String url = UriComponentsBuilder
                .fromHttpUrl(onchainSentimentUrl + "/api/onchain-sentiment/{symbol}")
                .buildAndExpand(symbol)
                .toUriString();
            
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new Exception("On-chain sentiment service returned empty response");
            }
        } catch (HttpClientErrorException | HttpServerErrorException e) {
            String errorMessage = extractErrorMessage(e.getResponseBodyAsString());
            throw new Exception("On-chain sentiment analysis failed: " + errorMessage, e);
        } catch (RestClientException e) {
            throw new Exception("Failed to connect to on-chain sentiment service: " + e.getMessage(), e);
        }
    }
    
    private String extractErrorMessage(String responseBody) {
        if (responseBody == null || responseBody.isEmpty()) {
            return "Unknown error";
        }
        if (responseBody.contains("\"detail\"")) {
            int detailStart = responseBody.indexOf("\"detail\"") + 9;
            int detailEnd = responseBody.indexOf("\"", detailStart);
            if (detailEnd > detailStart) {
                return responseBody.substring(detailStart, detailEnd);
            }
        }
        
        return responseBody;
    }
}