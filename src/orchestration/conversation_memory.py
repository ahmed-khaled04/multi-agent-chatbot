from collections import deque

from langchain_core.messages import BaseMessage, HumanMessage


class ConversationMemory:
    """Keep a bounded history of user and final assistant messages."""

    def __init__(self, max_turns: int = 5) -> None:
        if not isinstance(max_turns, int) or isinstance(max_turns, bool):
            raise TypeError("max_turns must be an integer")
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1")

        self.max_turns = max_turns
        self._turns: deque[tuple[HumanMessage, BaseMessage]] = deque(
            maxlen=max_turns
        )

    @property
    def turn_count(self) -> int:
        return len(self._turns)

    def messages_with(self, current_message: HumanMessage) -> list[BaseMessage]:
        """Return bounded history followed by the current user message."""
        messages: list[BaseMessage] = []
        for user_message, assistant_message in self._turns:
            messages.extend((user_message, assistant_message))
        messages.append(current_message)
        return messages

    def add_turn(
        self,
        user_message: HumanMessage,
        assistant_message: BaseMessage,
    ) -> None:
        self._turns.append((user_message, assistant_message))

    def clear(self) -> None:
        self._turns.clear()
