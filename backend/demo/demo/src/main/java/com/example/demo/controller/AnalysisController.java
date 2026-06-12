package com.example.demo.controller;

import com.example.demo.services.AnalysisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/analysis")
@CrossOrigin(origins = "https://clientdas15.z36.web.core.windows.net")
public class AnalysisController {

    @Autowired
    private AnalysisService analysisService;

    /**
     * Get technical analysis results for a symbol.
     *
     * @param symbol Crypto symbol (e.g., "BTC")
     * @param timeframe One of "1d", "1w", "1m" (default: "1d")
     */
    @GetMapping("/technical/{symbol}")
    public ResponseEntity<Map<String, Object>> getTechnicalAnalysis(
            @PathVariable String symbol,
            @RequestParam(defaultValue = "1d") String timeframe) {

        try {
            Map<String, Object> result = analysisService.getTechnicalAnalysis(symbol, timeframe);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Get LSTM price predictions for a symbol.
     *
     * @param symbol Crypto symbol (e.g., "BTC")
     * @param daysAhead Number of days to predict (default: 7)
     */
    @GetMapping("/lstm/{symbol}")
    public ResponseEntity<Map<String, Object>> getLSTMPrediction(
            @PathVariable String symbol,
            @RequestParam(defaultValue = "7") int daysAhead) {

        try {
            Map<String, Object> result = analysisService.getLSTMPrediction(symbol, daysAhead);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Get on-chain and sentiment analysis for a symbol.
     *
     * @param symbol Crypto symbol (e.g., "BTC")
     */
    @GetMapping("/onchain-sentiment/{symbol}")
    public ResponseEntity<Map<String, Object>> getOnChainSentiment(
            @PathVariable String symbol) {

        try {
            Map<String, Object> result = analysisService.getOnChainSentiment(symbol);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", e.getMessage()));
        }
    }
}