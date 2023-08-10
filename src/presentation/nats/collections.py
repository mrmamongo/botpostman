from typing import Any, Dict, Optional


class State:
    """
    An object that can be used to store arbitrary state.

    Used for `request.state` and `app.state`.
    """

    _state: Dict[str, Any]

    def __init__(self, state: Optional[Dict[str, Any]] = None):
        if state is None:
            state = {}
        super().__setattr__("_state", state)

    def __setattr__(self, key: str, value: Any) -> None:
        self._state[key] = value

    def __getattr__(self, key: str) -> Any:
        try:
            return self._state[key]
        except KeyError:
            message = "'{}' object has no attribute '{}'"
            raise AttributeError(message.format(self.__class__.__name__, key))

    def __delattr__(self, key: Any) -> None:
        del self._state[key]
