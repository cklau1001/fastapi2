from enum import Enum

class RequestStatus(Enum):
    QUEUED = "QUEUED"
    EXECUTING = "EXECUTING"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"