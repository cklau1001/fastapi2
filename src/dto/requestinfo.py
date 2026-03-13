"""
Use dataclass to streamline common methods (e.g. __init__, repr__, __eq__)
This class is used for JSON serialization, so avoiding any complex class type. (e.g. using str instead of RequestStatus)

"""
import logging

from datetime import datetime
from dataclasses import dataclass
from dto.taskinfo import TaskInfo
from service.logger import setup_logging

setup_logging()
log = logging.getLogger(__name__)

@dataclass
class RequestInfo:
    request_id: str = None
    workflow_name: str = None
    request_status: str = None  # use str, instead of RequestStatus to ensure that it is JSON serializable.
    start_time: datetime = None
    end_time: datetime = None
    remark: str = None
    taskinfo_list: list[TaskInfo] = None

