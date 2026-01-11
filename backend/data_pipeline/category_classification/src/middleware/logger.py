import logging
import json
from datetime import datetime
from typing import Any


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
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "service": "Category-Classifier-Worker",
                "pod": self.pod_name,
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
        self.logger.debug(self._log("DEBUG", event_type, message, **kwargs))
