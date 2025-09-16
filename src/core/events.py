# ============================================================================
# src/core/events.py
# ============================================================================
"""Event system for pub/sub architecture."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List
from datetime import datetime
import asyncio
import uuid


class Event(BaseModel):
    """Base event model."""
    model_config = ConfigDict(frozen=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    source: str
    data: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None


class PriceUpdateEvent(Event):
    """Price update event."""
    event_type: str = "price_update"


class OrderCreatedEvent(Event):
    """Order created event."""
    event_type: str = "order_created"


class OrderFilledEvent(Event):
    """Order filled event."""
    event_type: str = "order_filled"


class PositionUpdatedEvent(Event):
    """Position updated event."""
    event_type: str = "position_updated"


class RiskAlertEvent(Event):
    """Risk alert event."""
    event_type: str = "risk_alert"


class EventHandler(ABC):
    """Abstract event handler."""
    
    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Handle an event."""
        pass


class EventBus:
    """Event bus for publish/subscribe pattern."""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._queue = asyncio.Queue()
        self._running = False
    
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    async def publish(self, event: Event) -> None:
        """Publish an event."""
        await self._queue.put(event)
    
    async def start(self) -> None:
        """Start the event processing loop."""
        self._running = True
        while self._running:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                # Continue loop on timeout
                continue
            except Exception as e:
                # Log error but continue processing
                print(f"Error processing event: {e}")
    
    async def stop(self) -> None:
        """Stop the event processing loop."""
        self._running = False
    
    async def _process_event(self, event: Event) -> None:
        """Process a single event."""
        handlers = self._handlers.get(event.event_type, [])
        if handlers:
            tasks = [handler.handle(event) for handler in handlers]
            await asyncio.gather(*tasks, return_exceptions=True)


# Global event bus instance
event_bus = EventBus()