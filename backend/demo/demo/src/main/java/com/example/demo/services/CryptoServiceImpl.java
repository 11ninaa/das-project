package com.example.demo.services;

import com.example.demo.model.Crypto;
import com.example.demo.repository.CryptoRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Crypto service implementation.
 */
@Service
public class CryptoServiceImpl implements CryptoService {

    private final CryptoRepository stockPriceRepository;

    public CryptoServiceImpl(CryptoRepository stockPriceRepository) {
        this.stockPriceRepository = stockPriceRepository;
    }

    @Override
    public Page<Crypto> getAllStockPrices(Pageable pageable) {
        return stockPriceRepository.findAll(pageable);
    }

    @Override
    public Optional<Crypto> getStockPriceById(Long id) {
        return stockPriceRepository.findById(id);
    }

    @Override
    public Crypto saveStockPrice(Crypto stockPrice) {
        return stockPriceRepository.save(stockPrice);
    }

    @Override
    public Optional<Crypto> updateStockPrice(Long id, Crypto stockPriceDetails) {
        return stockPriceRepository.findById(id).map(existing -> {
            existing.setSymbol(stockPriceDetails.getSymbol());
            existing.setBase_asset(stockPriceDetails.getBase_asset());
            existing.setQuote_asset(stockPriceDetails.getQuote_asset());
            existing.setSource(stockPriceDetails.getSource());
            existing.setDate(stockPriceDetails.getDate());
            existing.setOpen(stockPriceDetails.getOpen());
            existing.setHigh(stockPriceDetails.getHigh());
            existing.setLow(stockPriceDetails.getLow());
            existing.setClose(stockPriceDetails.getClose());
            existing.setVolume(stockPriceDetails.getVolume());
            existing.setQuote_volume(stockPriceDetails.getQuote_volume());
            existing.setNumber_of_trades(stockPriceDetails.getNumber_of_trades());
            return stockPriceRepository.save(existing);
        });
    }

    @Override
    public boolean deleteStockPrice(Long id) {
        return stockPriceRepository.findById(id).map(record -> {
            stockPriceRepository.delete(record);
            return true;
        }).orElse(false);
    }


    @Override
    public List<Crypto> getStockPricesBySymbol(String symbol) {
        return stockPriceRepository.findBySymbolIgnoreCase(
                symbol,
                org.springframework.data.domain.PageRequest.of(0, 100)
        ).getContent();
    }
    @Override
    public Optional<Crypto> getStockPriceBySymbolAndDate(String symbol, String date) {
        return stockPriceRepository.findBySymbolAndDate(symbol, date);
    }

    @Override
    public Optional<Crypto> getMostRecentStockPriceBySymbol(String symbol) {
        return stockPriceRepository.findMostRecentBySymbol(symbol);
    }

    @Override
    public List<Crypto> getStockPricesBySymbolAndDateRange(String symbol, String fromDate, String toDate) {
        return stockPriceRepository.findBySymbolAndDateBetween(symbol, fromDate, toDate);
    }

    @Override
    public List<String> getAllSources() {
        return stockPriceRepository.findDistinctSources();
    }

    @Override
    public List<Crypto> getTrendingStocks(int limit) {
        List<Crypto> latestStocks = stockPriceRepository.findLatestPerSymbol();

        return latestStocks.stream()
                .filter(stock -> stock.getSymbol() != null && stock.getQuote_volume() > 0)
                .sorted((a, b) -> Double.compare(b.getQuote_volume(), a.getQuote_volume()))
                .limit(limit)
                .collect(Collectors.toList());
    }

    @Override
    public Page<Crypto> searchByExactSymbol(String symbol, Pageable pageable) {
        if (symbol == null || symbol.trim().isEmpty()) {
            return stockPriceRepository.findAll(pageable);
        }
        return stockPriceRepository.findBySymbolIgnoreCase(symbol.trim(), pageable);
    }

    @Override
    public Page<Crypto> searchByExactSymbols(List<String> symbols, Pageable pageable) {
        if (symbols == null || symbols.isEmpty()) {
            return stockPriceRepository.findAll(pageable);
        }
        return stockPriceRepository.findBySymbolInIgnoreCase(symbols, pageable);
    }

}

