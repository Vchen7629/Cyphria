import logging
import json
from datetime import datetime
from typing import Any


class StructuredLogger:
    """Central Logging for this worker service"""

    def __init__(self, pod: str) -> None:
        self.pod_name = pod

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()  # logs to stdout
        handler.setFormatter(logging.Formatter("%(message)s"))  # just output JSON
        self.logger.addHandler(handler)

    def _log(self, level: str, event_type: str, message: str, **kwargs: Any) -> str:
        """
        log message json object containing all relevant info in the log

        Args:
            level: either info, error, debug
            event_type: the event (component) that triggered this
            message: the log message describing what happened
            **kwargs: extra arguments

        Returns
            str: the whole log json as a string
        """
        return json.dumps(
            {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "service": "Api-Ingestion-Worker",
                "pod": self.pod_name,
                "event_type": event_type,
                "message": message,
                **kwargs,
            }
        )

    def info(self, event_type: str, message: str, **kwargs: Any) -> None:
        """
        Info log event

        Args:
            event_type: the event type that triggered this
            message: log message describing the log
            **kwargs: extra arguments
        """
        self.logger.info(self._log("INFO", event_type, message, **kwargs))
    
    
    def warning(self, event_type: str, message: str, **kwargs: Any) -> None:
        """
        Warning log event

        Args:
            event_type: the event type that triggered this
            message: log message describing the log
            **kwargs: extra arguments
        """
        self.logger.warning(self._log("WARNING", event_type, message, **kwargs))

    def error(self, event_type: str, message: str, **kwargs: Any) -> None:
        """
        error log event

        Args:
            event_type: the event type that triggered this
            message: log message describing the log
            **kwargs: extra arguments
        """
        self.logger.error(self._log("ERROR", event_type, message, **kwargs))

    def debug(self, event_type: str, message: str, **kwargs: Any) -> None:
        """
        debug log event

        Args:
            event_type: the event type that triggered this
            message: log message describing the log
            **kwargs: extra arguments
        """
        self.logger.debug(self._log("DEBUG", event_type, message, **kwargs))
