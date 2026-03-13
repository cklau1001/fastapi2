from pydantic import BaseModel
from datetime import datetime

class TopWorkflowRequestSchema(BaseModel):
    workflow_name: str | None

class WorkflowRequestSchema(TopWorkflowRequestSchema):
    request_id: str | None

class TopWorkflowResponseSchema(BaseModel):
    request_id: str | None = None
    workflow_name: str | None = None
    request_status: str | None = None

class WorkflowResponseSchema(TopWorkflowResponseSchema):
    start_time: datetime | None = None
    end_time: datetime | None = None
