class LogEntry:
    """Represents a single entry within the log, storing its timestamp, scope and
    message. This makes it easier to select certain log entries using the
    Logger.get() method.
    """
    def __init__(
        self: object, message: str, output: bool, scope: str, timestamp: str
    ) -> None:
        self.message = message
        self.output = output
        self.scope = scope
        self.timestamp = timestamp
        self.rendered = (
            f"[{timestamp}] {scope}: {message}"
            if scope != "NOSCOPE" else
            f"{message}"
        )