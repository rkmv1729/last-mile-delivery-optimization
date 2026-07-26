"""
Simulation Scheduler
--------------------
Controls the execution timing of simulation events.

The scheduler manages simulation time, scheduled events,
and determines when simulation managers should run.
"""

import heapq

from __future__ import annotations

from datetime import datetime, timedelta
import logging

from typing import Callable

from simulation_engine.state import SimulationState

from simulation_engine.event import (
    EventType,
    SimulationEvent,
)

logger = logging.getLogger(__name__)

class SimulationScheduler:
    """
    Event scheduler for the simulation engine.
    """

    def __init__(self, 
        speed=1
    ):

        self.speed = speed

        self.running = False

        self.event_queue: list[SimulationEvent] = []

        self.handlers: dict[
            EventType,
            Callable[[SimulationEvent], None],
        ] = {}

        self.periodic_intervals = {
            EventType.FORECAST: timedelta(minutes=15),
            EventType.DISPATCH: timedelta(minutes=10),
            EventType.ASSIGNMENT: timedelta(minutes=5),
        }

    # ---------------------------------------------------------
    # Clock
    # ---------------------------------------------------------

    def tick(
        self,
        delta: timedelta,
    ) -> None:
        """
        Advance simulation by one tick.
        """

        scaled_delta = timedelta(
            seconds=delta.total_seconds() * self.speed
        )

        self.advance_time(scaled_delta)

        self.process_due_events()

    # ---------------------------------------------------------
    # Event Queue
    # ---------------------------------------------------------

    # initialize periodic events
    def initialize_periodic_events(self) -> None:
        """
        Schedule the first periodic events.
        """

        self.schedule_periodic_event(
            EventType.FORECAST,
            priority=7,
        )

        self.schedule_periodic_event(
            EventType.DISPATCH,
            priority=6,
        )

        self.schedule_periodic_event(
            EventType.ASSIGNMENT,
            priority=5,
        )

    def schedule_event(
        self,
        event: SimulationEvent,
    ) -> None:
        """
        Insert event into priority queue.
        """

        heapq.heappush(
            self.event_queue,
            event,
        )

    def execute_event(
        self,
        event: SimulationEvent,
    ) -> None:
        """
        Execute an event using its registered handler.
        """

        handler = self.handlers.get(
            event.event_type,
        )

        if handler is None:

            logger.warning(
                "No handler registered for %s",
                event.event_type.value,
            )

            return

        handler(event)

        if event.event_type in self.periodic_intervals:

            self.schedule_periodic_event(
                event_type=event.event_type,
                priority=event.priority,
                start_time=event.scheduled_time,
            )

    def process_due_events(
        self,
        state: SimulationState
    ) -> None:
        """
        Execute all events due at the current simulation time.
        """

        while self.event_queue:

            event = self.peek_event()

            if event is None:
                break

            if event.scheduled_time > state.current_time:
                break

            event = self.next_event()

            self.execute_event(event)

    # Register handlers

    def register_handler(
        self,
        event_type: EventType,
        handler: Callable[[SimulationEvent], None],
    ) -> None:
        """
        Register callback for an event type.
        """

        self.handlers[event_type] = handler

    # Peek event
    def peek_event(
        self,
    ) -> SimulationEvent | None:

        if not self.event_queue:
            return None

        return self.event_queue[0]

    # Pop event
    def next_event(
        self,
    ) -> SimulationEvent | None:

        if not self.event_queue:
            return None

        return heapq.heappop(self.event_queue)

    # Advance time
    def advance_time(
        self,
        delta: timedelta,
    ) -> None:
        """
        Advance simulation clock.
        """

        self.current_time += delta

    # Generic periodic scheduler
    def schedule_periodic_event(
        self,
        state: SimulationState,
        event_type: EventType,
        priority: int,
        start_time: datetime | None = None,
    ) -> None:
        """
        Schedule the next occurrence of a periodic event.
        """

        if start_time is None:
            start_time = state.current_time

        interval = self.periodic_intervals[event_type]

        self.schedule_event(
            SimulationEvent(
                scheduled_time=start_time + interval,
                priority=priority,
                event_type=event_type,
            )
        )

    def run(
        self,
        tick_interval: timedelta,
    ) -> None:
        """
        Run the scheduler until stopped.
        """

        self.start()

        while self.running:

            self.tick(tick_interval)


    # ---------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------

    # Queue utilities
    def clear(self) -> None:

        self.event_queue.clear()


    def queue_size(self) -> int:

        return len(self.event_queue)


    def has_events(self) -> bool:

        return bool(self.event_queue)

    # Scheduler control

    def start(self) -> None:

        self.running = True


    def stop(self) -> None:

        self.running = False

    def get_status(self, state: SimulationState):
        """
        Return scheduler status.
        """

        return {
            "tick": state.tick,
            "simulation_time": state.current_time,
            "pending_events": len(self.event_queue),
        }