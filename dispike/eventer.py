from dispike.errors.events import InvalidEventType
import typing
from loguru import logger
import inspect
from enum import Enum


class EventTypes(str, Enum):
    COMMAND = "command"
    COMPONENT = "component"


class EventHandler(object):

    """A relatively simple "event handler". Pass in async functions and provide a string, and it will call it

    Attributes:
        callbacks (dict): dict of names --> functions
    """

    def __init__(self):
        self.callbacks = {"command": {}, "component": {}}

    def on(
        self,
        event: str,
        type: EventTypes = EventTypes.COMMAND,
        func: typing.Callable = None,
    ):
        """A wrapper over an async function, registers it in .callbacks.

        Args:
            event (str): Event name
            type (EventTypes): Type of this event.
            func (None, optional): function to wrap around

        Returns:
            <function>: returns the wrapped function
        """

        if not isinstance(type, EventTypes):
            if isinstance(type, str):  # pragma: no cover
                logger.warning(
                    "Passing a unknown EventType, this may cause issues and is unsupported"
                )  # noqa
            else:
                # TODO: Maybe it's not good to overrwrite a default python function. Maybe change type to a different value?
                raise InvalidEventType(type)  # pragma: no cover

        def on(func):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Function must be a async function.")

            if event not in self.callbacks[type]:
                logger.debug(f"Added {event} to corresponding function to {func}")
                self.callbacks[type][event] = {
                    "settings": {},
                    "function": func,
                }
            else:
                raise TypeError("Events can only have one corresponding handler.")

            return func

        return on(func) if func else on

    def check_event_exists(self, event: str, type: str) -> bool:
        """Checks if the event in ``.callbacks``

        Args:
            event (str): event name

        Returns:
            bool: returns if the event is in callbacks.
        """
        return event in self.callbacks[type]

    def return_event_settings(self, event: str, type: str) -> dict:
        if self.check_event_exists(event, type):
            return self.callbacks[type][event]["settings"]
        raise TypeError(
            f"Event {event} is not in callbacks. Did you register this event?"
        )

    def return_event_function(self, event: str, type: str) -> dict:
        if self.check_event_exists(event, type):
            return self.callbacks[type][event]["function"]
        raise TypeError(
            f"Event {event} is not in callbacks. Did you register this event?"
        )

    def view_event_function_return_type(self, event: str, type: str) -> dict:
        """Get type hint for event functions

        Args:
            event (str): Event name

        Returns:
            dict: Returns .get_type_hints for event
        """
        return typing.get_type_hints(self.callbacks[type][event]["function"])

    async def emit(self, event: str, type: str, *args, **kwargs):
        """'Emits' an event. It will basically call the function from .callbacks and return the function result

        Args:
            event (str): Event name
            type (str): Event type
            *args: extra arguments to pass
            **kwargs: extra kwargs to pass

        Returns:
            function result: returns the function result

        Raises:
            TypeError: raises if event is not registered.
        """
        if event not in self.callbacks[type]:
            raise TypeError(
                f"event {event} does not have a corresponding handler. Did you register this function/event?"
            )

        _look_up_function = self.return_event_function(event, type)
        return await _look_up_function(*args, **kwargs)
