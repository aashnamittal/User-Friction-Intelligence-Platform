package com.ufip.api.models;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "recovery_recommendations")
@Data
@NoArgsConstructor
public class RecoveryRecommendation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "cohort_id")
    private Long cohortId;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String recommendation;

    @Column(nullable = false, length = 50)
    private String status = "Pending";

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt = LocalDateTime.now();
}
