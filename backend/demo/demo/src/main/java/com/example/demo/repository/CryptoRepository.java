package com.example.demo.repository;

import com.example.demo.model.Crypto;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Spring Data JPA repository for Crypto entities.
 */
@Repository
public interface CryptoRepository extends JpaRepository<Crypto, Long> {

    List<Crypto> findBySymbol(String symbol);
    List<Crypto> findBySymbolAndDateBetween(String symbol, String startDate, String endDate);
    List<Crypto> findByVolumeGreaterThan(long volume);
    List<Crypto> findBySource(String source);

    @Query("SELECT s FROM Crypto s WHERE UPPER(s.symbol) = UPPER(:symbol)")
    Page<Crypto> findBySymbolIgnoreCase(@Param("symbol") String symbol, Pageable pageable);

    @Query("SELECT s FROM Crypto s WHERE UPPER(s.symbol) IN :symbols")
    Page<Crypto> findBySymbolInIgnoreCase(@Param("symbols") List<String> symbols, Pageable pageable);

    Optional<Crypto> findBySymbolAndDate(String symbol, String date);

    @Query("SELECT DISTINCT s.source FROM Crypto s WHERE s.source IS NOT NULL")
    List<String> findDistinctSources();

    @Query("SELECT s FROM Crypto s WHERE s.symbol = :symbol ORDER BY s.date DESC LIMIT 1")
    Optional<Crypto> findMostRecentBySymbol(@Param("symbol") String symbol);

    @Query("SELECT c FROM Crypto c WHERE c.date IN " +
            "(SELECT MAX(c2.date) FROM Crypto c2 GROUP BY c2.symbol)")
    List<Crypto> findLatestPerSymbol();
}
