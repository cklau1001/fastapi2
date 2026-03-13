import logging
from dataclasses import dataclass
from datetime import datetime

from service.logger import setup_logging

setup_logging()
log = logging.getLogger(__name__)

@dataclass
class TaskInfo:
    task_id: str = None
    task_name: str = None
    request_id: str = None
    workflow_name: str = None
    step_id: str = None
    start_time: datetime = None
    end_time: datetime = None
    next_retry_at: datetime = None
    task_status: str = None
    retry_count: int = 0

