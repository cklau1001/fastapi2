from enum import Enum

class TaskStatus(Enum):
    QUEUED = "QUEUED"
    EXECUTNG = "EXECUTING"
    SUSPENDED = "SUSPENDED"
    RETRY = "RETRY"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
