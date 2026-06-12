package com.example.demo.services;

import com.example.demo.model.Crypto;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Optional;

/**
 * Service interface for crypto price operations.
 */
public interface CryptoService {
    
    Page<Crypto> getAllStockPrices(Pageable pageable);
    Optional<Crypto> getStockPriceById(Long id);
    Crypto saveStockPrice(Crypto stockPrice);
    Optional<Crypto> updateStockPrice(Long id, Crypto stockPriceDetails);
    boolean deleteStockPrice(Long id);
    List<Crypto> getStockPricesBySymbol(String symbol);
    Page<Crypto> searchByExactSymbol(String symbol, Pageable pageable);
    Page<Crypto> searchByExactSymbols(List<String> symbols, Pageable pageable);
    Optional<Crypto> getStockPriceBySymbolAndDate(String symbol, String date);
    Optional<Crypto> getMostRecentStockPriceBySymbol(String symbol);
    List<Crypto> getStockPricesBySymbolAndDateRange(String symbol, String fromDate, String toDate);
    List<String> getAllSources();
    List<Crypto> getTrendingStocks(int limit);
}
