class LogEntry:
    """
    Represents a single log entry, storing its timestamp, scope and message.
    """
    def __init__(self: object, message: str, output: bool, scope: str, timestamp: str) -> None:
        self.message = message
        self.output = output
        self.scope = scope
        self.timestamp = timestamp
        self.rendered = (
            f"[{timestamp}] {scope}: {message}"
            if scope != "NOSCOPE" else
            f"{message}"
        )