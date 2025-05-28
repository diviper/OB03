"""
Module containing event-related classes for the zoo management system.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List, Optional, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Animal
    from .staff import Staff

class EventType(Enum):
    """Types of events that can occur in the zoo."""
    FEEDING = auto()
    MEDICAL_CHECK = auto()
    TOUR = auto()
    SHOW = auto()
    CLEANING = auto()
    ENRICHMENT = auto()


class EventObserver(Protocol):
    """Protocol for objects that can observe events."""
    def notify(self, event: 'ZooEvent') -> None:
        """Handle notification of an event."""
        ...


@dataclass
class ZooEvent:
    """Class representing an event in the zoo."""
    event_type: EventType
    name: str
    description: str
    start_time: datetime
    duration: timedelta
    location: str
    staff: List[Staff] = field(default_factory=list)
    animals: List[Animal] = field(default_factory=list)
    observers: List[EventObserver] = field(default_factory=list, init=False)
    
    def add_observer(self, observer: EventObserver) -> None:
        """Add an observer to this event."""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: EventObserver) -> None:
        """Remove an observer from this event."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self) -> None:
        """Notify all observers about this event."""
        for observer in self.observers:
            observer.notify(self)
    
    @property
    def end_time(self) -> datetime:
        """Calculate and return the end time of the event."""
        return self.start_time + self.duration
    
    def is_ongoing(self, when: Optional[datetime] = None) -> bool:
        """Check if the event is ongoing at the given time (defaults to now)."""
        when = when or datetime.now()
        return self.start_time <= when <= self.end_time
    
    def __str__(self) -> str:
        return (
            f"{self.name} ({self.event_type.name})\n"
            f"Time: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}\n"
            f"Location: {self.location}\n"
            f"Staff: {', '.join(s.name for s in self.staff)}\n"
            f"Animals: {', '.join(a.name for a in self.animals) if self.animals else 'None'}\n"
            f"{self.description}"
        )


class FeedingEvent(ZooEvent):
    """Event representing an animal feeding."""
    
    def __init__(
        self,
        name: str,
        start_time: datetime,
        location: str,
        food_type: str,
        animals: List[Animal],
        staff: List[Staff],
        duration: timedelta = timedelta(minutes=30),
        description: str = ""
    ):
        description = description or f"Feeding time with {food_type}!"
        super().__init__(
            event_type=EventType.FEEDING,
            name=name,
            description=description,
            start_time=start_time,
            duration=duration,
            location=location,
            staff=staff,
            animals=animals
        )
        self.food_type = food_type
    
    def __str__(self) -> str:
        return (
            f"🍽️ {self.name} - {self.start_time.strftime('%H:%M')}\n"
            f"Feeding {', '.join(a.name for a in self.animals)} with {self.food_type}\n"
            f"Location: {self.location} | Staff: {', '.join(s.name for s in self.staff)}"
        )


class MedicalCheckEvent(ZooEvent):
    """Event representing a medical check for animals."""
    
    def __init__(
        self,
        name: str,
        start_time: datetime,
        location: str,
        animals: List[Animal],
        staff: List[Staff],
        duration: timedelta = timedelta(minutes=60),
        description: str = ""
    ):
        description = description or "Routine medical check-up"
        super().__init__(
            event_type=EventType.MEDICAL_CHECK,
            name=name,
            description=description,
            start_time=start_time,
            duration=duration,
            location=location,
            staff=staff,
            animals=animals
        )
    
    def __str__(self) -> str:
        return (
            f"🏥 {self.name} - {self.start_time.strftime('%H:%M')}\n"
            f"Medical check for {', '.join(a.name for a in self.animals)}\n"
            f"Location: {self.location} | Vet: {', '.join(s.name for s in self.staff)}"
        )


class TourEvent(ZooEvent):
    """Event representing a guided tour in the zoo."""
    
    def __init__(
        self,
        name: str,
        start_time: datetime,
        location: str,
        staff: List[Staff],
        duration: timedelta = timedelta(hours=1),
        description: str = "",
        max_visitors: int = 20
    ):
        description = description or "Guided tour of the zoo"
        super().__init__(
            event_type=EventType.TOUR,
            name=name,
            description=description,
            start_time=start_time,
            duration=duration,
            location=location,
            staff=staff,
            animals=[]
        )
        self.max_visitors = max_visitors
        self.visitor_count = 0
    
    def add_visitors(self, count: int) -> bool:
        """Add visitors to the tour if there's space."""
        if self.visitor_count + count <= self.max_visitors:
            self.visitor_count += count
            return True
        return False
    
    def __str__(self) -> str:
        return (
            f"🚶 {self.name} - {self.start_time.strftime('%H:%M')}\n"
            f"Guided tour with {', '.join(s.name for s in self.staff)}\n"
            f"Location: {self.location} | Visitors: {self.visitor_count}/{self.max_visitors}"
        )
