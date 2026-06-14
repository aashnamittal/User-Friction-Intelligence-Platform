package com.ufip.api.repositories;

import com.ufip.api.models.Event;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface EventRepository extends JpaRepository<Event, Long> {
    
    @Query(value = "SELECT e.* FROM events e ORDER BY e.created_at DESC LIMIT 50", nativeQuery = true)
    List<Event> findLatestEvents();
}
