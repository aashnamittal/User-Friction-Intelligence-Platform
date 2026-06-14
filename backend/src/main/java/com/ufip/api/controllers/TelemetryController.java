package com.ufip.api.controllers;

import com.ufip.api.models.Event;
import com.ufip.api.repositories.EventRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/telemetry")
public class TelemetryController {

    @Autowired
    private EventRepository eventRepository;

    @GetMapping("/logs")
    public List<Event> getLatestLogs() {
        return eventRepository.findLatestEvents();
    }
}
