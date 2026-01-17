import logging
from typing import Any

def on_task_failure(context: Any) -> None:
    """Log failure details, alerting in the future"""
    task_instance = context['task_instance']
    logging.error(f"Task {task_instance.task_id} failed")
    
    # could add alerting like slack notifications, discord notifications, etc