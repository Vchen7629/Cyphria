# Todo: code for handling error/info logging
import logging, time, json
from datetime import datetime

# Central Logging for this worker service
class StructuredLogger:
    def __init__(self, pod: None):
        self.pod_name = pod

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()  # logs to stdout
        handler.setFormatter(logging.Formatter("%(message)s"))  # just output JSON
        self.logger.addHandler(handler)
    
    def _log(self, level: str, event_type: str, message: str, **kwargs):
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "service": "Topic-Classification-Worker",
            "pod": self.pod_name,
            "event_type": event_type,
            "message": message,
            **kwargs
        })

    # log levels
    def info(self, event_type: str, message: str, **kwargs):
        self.logger.info(self._log("INFO", event_type, message, **kwargs))

    def error(self, event_type: str, message: str, **kwargs):
        self.logger.error(self._log("ERROR", event_type, message, **kwargs))
    
    def debug(self, event_type: str, message: str, **kwargs):
        self.logger.info(self._log("DEBUG", event_type, message, **kwargs))

