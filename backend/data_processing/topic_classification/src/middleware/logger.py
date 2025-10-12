# Todo: code for handling error/info logging
import logging
from datetime import datetime
from typing import Any
import json


# Central Logging for this worker service
class StructuredLogger:
    def __init__(self, pod: str) -> None:
        self.pod_name = pod

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()  # logs to stdout
        handler.setFormatter(logging.Formatter("%(message)s"))  # just output JSON
        self.logger.addHandler(handler)

    def _log(self, level: str, event_type: str, message: str, **kwargs: Any) -> str:
        return json.dumps(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "service": "Topic-Classification-Worker",
                "event_type": event_type,
                "message": message,
                **kwargs,
            }
        )

    # log levels
    def info(self, event_type: str, message: str, **kwargs: Any) -> None:
        self.logger.info(self._log("INFO", event_type, message, **kwargs))

    def error(self, event_type: str, message: str, **kwargs: Any) -> None:
        self.logger.error(self._log("ERROR", event_type, message, **kwargs))

    def debug(self, event_type: str, message: str, **kwargs: Any) -> None:
        self.logger.info(self._log("DEBUG", event_type, message, **kwargs))
