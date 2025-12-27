"""
Event bus for decoupled communication
"""
from typing import Callable, Dict, List, Any
from enum import Enum


class EventType(str, Enum):
    """Event types"""
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
    INTEGRATION_CONNECTED = "integration.connected"
    INTEGRATION_DISCONNECTED = "integration.disconnected"


EventHandlers = Dict[EventType, List[Callable[[Any], None]]]


class EventBus:
    """Simple event bus implementation"""
    
    def __init__(self):
        self._handlers: EventHandlers = {}
    
    def subscribe(self, event_type: EventType, handler: Callable[[Any], None]):
        """Subscribe to an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: EventType, handler: Callable[[Any], None]):
        """Unsubscribe from an event type"""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    async def emit(self, event_type: EventType, data: Any = None):
        """Emit an event"""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    if callable(handler):
                        # Support both sync and async handlers
                        import asyncio
                        if asyncio.iscoroutinefunction(handler):
                            await handler(data)
                        else:
                            handler(data)
                except Exception as e:
                    # Log error but don't stop other handlers
                    print(f"Error in event handler for {event_type}: {e}")


# Global event bus instance
event_bus = EventBus()

