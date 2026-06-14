package com.ufip.api.models;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "friction_scores")
@Data
@NoArgsConstructor
public class FrictionScore {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(nullable = false)
    private Double score;

    @Column(name = "rage_clicks", nullable = false)
    private Integer rageClicks = 0;

    @Column(name = "error_count", nullable = false)
    private Integer errorCount = 0;

    @Column(name = "avg_latency", nullable = false)
    private Double avgLatency = 0.0;

    @Column(name = "checkout_abandoned", nullable = false)
    private Boolean checkoutAbandoned = false;

    @Column(name = "calculated_at", nullable = false)
    private LocalDateTime calculatedAt = LocalDateTime.now();
}
