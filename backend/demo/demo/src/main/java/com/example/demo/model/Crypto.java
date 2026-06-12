package com.example.demo.model;

import jakarta.persistence.*;
import lombok.*;
import java.io.Serializable;
import java.util.Date;

/**
 * Cryptocurrency price record entity.
 */
@Data
@Entity
@Table(name = "crypto_prices")
@NoArgsConstructor
@AllArgsConstructor
public class Crypto implements Serializable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String symbol;
    private String base_asset;
    private String quote_asset;
    private String source;
    private String date;

    private double open;
    private double high;
    private double low;
    private double close;
    
    private long volume;
    private double quote_volume;
    private long number_of_trades;

    @Temporal(TemporalType.TIMESTAMP)
    @Column(nullable = false, updatable = false)
    private Date created_at;

    @Temporal(TemporalType.TIMESTAMP)
    private Date updated_at;

    @PrePersist
    protected void onCreate() {
        this.created_at = new Date();
        this.updated_at = new Date();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updated_at = new Date();
    }

}
