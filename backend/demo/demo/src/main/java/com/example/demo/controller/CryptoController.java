package com.example.demo.controller;

import com.example.demo.model.Crypto;
import com.example.demo.services.CryptoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * REST controller for crypto price data operations.
 */
@RestController
@RequestMapping("/api/crypto")
@CrossOrigin(origins = "https://clientdas15.z36.web.core.windows.net")
public class CryptoController {

    @Autowired
    private CryptoService cryptoService;

    /**
     * Search for crypto assets by symbol. Supports multiple comma-separated symbols.
     *
     * @param symbol The symbol(s) to search for (comma-separated for multiple symbols)
     * @param page Page number (0-indexed, default: 0)
     * @param size Number of records per page (default: 20)
     */
    @GetMapping("/search")
    public ResponseEntity<Page<Crypto>> search(
            @RequestParam(required = false) String symbol,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {

        PageRequest pageRequest = PageRequest.of(page, size);

        if (symbol == null || symbol.trim().isEmpty()) {
            Page<Crypto> results = cryptoService.getAllStockPrices(pageRequest);
            return ResponseEntity.ok(results);
        }

        String trimmedSymbol = symbol.trim();

        if (trimmedSymbol.contains(",")) {
            List<String> symbols = Arrays.stream(trimmedSymbol.split(","))
                    .map(String::trim)
                    .filter(s -> !s.isEmpty())
                    .map(String::toUpperCase)
                    .collect(Collectors.toList());

            if (symbols.isEmpty()) {
                return ResponseEntity.ok(Page.empty(pageRequest));
            }

            Page<Crypto> results = cryptoService.searchByExactSymbols(symbols, pageRequest);
            return ResponseEntity.ok(results);
        } else {
            Page<Crypto> results = cryptoService.searchByExactSymbol(trimmedSymbol, pageRequest);
            return ResponseEntity.ok(results);
        }
    }


    /**
     * Get list of all distinct exchange sources.
     */
    @GetMapping("/exchanges")
    public ResponseEntity<List<String>> getExchanges() {
        List<String> sources = cryptoService.getAllSources();
        return ResponseEntity.ok(sources);
    }

    /**
     * Get historical price data for a symbol within a date range.
     *
     * @param symbol The crypto symbol (e.g., "BTCUSDT")
     * @param from Start date (inclusive) in YYYY-MM-DD format
     * @param to End date (inclusive) in YYYY-MM-DD format
     * @param source Optional exchange source filter
     */
    @GetMapping("/{symbol}/history")
    public ResponseEntity<List<Crypto>> getHistory(
            @PathVariable String symbol,
            @RequestParam String from,
            @RequestParam String to,
            @RequestParam(required = false) String source) {

        String decodedSymbol = decodeSymbol(symbol);
        List<Crypto> history = cryptoService.getStockPricesBySymbolAndDateRange(
                decodedSymbol, from, to);

        if (source != null && !source.trim().isEmpty()) {
            history = history.stream()
                    .filter(sp -> sp.getSource() != null && sp.getSource().equals(source))
                    .collect(Collectors.toList());
        }

        return ResponseEntity.ok(history);
    }

    /**
     * Get crypto price data for a symbol. Returns most recent if no date provided.
     *
     * @param symbol The crypto symbol (e.g., "BTCUSDT")
     * @param date Optional date parameter in YYYY-MM-DD format
     */
    @GetMapping("/{symbol}")
    public ResponseEntity<Crypto> getCrypto(
            @PathVariable String symbol,
            @RequestParam(required = false) String date) {

        String decodedSymbol = decodeSymbol(symbol);

        if (date != null && !date.trim().isEmpty()) {
            Optional<Crypto> result = cryptoService.getStockPriceBySymbolAndDate(decodedSymbol, date);
            return result.map(ResponseEntity::ok)
                    .orElse(ResponseEntity.notFound().build());
        } else {
            Optional<Crypto> result = cryptoService.getMostRecentStockPriceBySymbol(decodedSymbol);
            return result.map(ResponseEntity::ok)
                    .orElse(ResponseEntity.notFound().build());
        }
    }

    /**
     * Get trending crypto assets sorted by quote volume.
     *
     * @param limit Maximum number of results to return (default: 10)
     */
    @GetMapping("/trending")
    public ResponseEntity<List<Crypto>> getTrending(
            @RequestParam(defaultValue = "10") int limit) {
        List<Crypto> trending = cryptoService.getTrendingStocks(limit);
        return ResponseEntity.ok(trending);
    }

    /**
     * Decode URL-encoded symbols.
     */
    private String decodeSymbol(String symbol) {
        try {
            return URLDecoder.decode(symbol, StandardCharsets.UTF_8);
        } catch (Exception e) {
            return symbol;
        }
    }
}

