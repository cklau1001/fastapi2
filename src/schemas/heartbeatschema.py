from pydantic import BaseModel
from datetime import datetime

class HeartBeatResponse(BaseModel):
    time: datetime
    IP: str
    message: str