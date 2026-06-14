package com.ufip.api.models;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "user_cohorts")
@Data
@NoArgsConstructor
public class UserCohort {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "cohort_label", nullable = false, length = 100)
    private String cohortLabel;

    @Column(name = "cluster_id", nullable = false)
    private Integer clusterId;

    @Column(name = "assigned_at", nullable = false)
    private LocalDateTime assignedAt = LocalDateTime.now();
}
