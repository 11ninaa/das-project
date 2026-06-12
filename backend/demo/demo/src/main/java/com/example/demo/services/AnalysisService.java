package com.example.demo.services;

import java.util.Map;

public interface AnalysisService {
    Map<String, Object> getTechnicalAnalysis(String symbol, String timeframe) throws Exception;

    Map<String, Object> getLSTMPrediction(String symbol, int daysAhead) throws Exception;

    Map<String, Object> getOnChainSentiment(String symbol) throws Exception;
}