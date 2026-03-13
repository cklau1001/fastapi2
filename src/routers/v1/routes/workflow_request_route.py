"""
Leverage global error handler in main.py for any exception handling

"""

from fastapi import APIRouter, Response, status

from schemas.workflow_request_schema import (TopWorkflowRequestSchema, TopWorkflowResponseSchema,
                                             WorkflowResponseSchema)
from dto.requestinfo import RequestInfo
from service.requestservice import request_service   # Inject singleton into target route
from service.requeststatus import RequestStatus
from otel.otel_config import tracer, trace, baggage, set_baggage_context, otelspan

router = APIRouter(
    prefix = "/workflow",
    tags = ["workflow"],
    responses = {
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

@router.post(
    "/request",
    description="Initiate a new workflow request",
    response_model=TopWorkflowResponseSchema,
    status_code=status.HTTP_202_ACCEPTED
)

@tracer.start_as_current_span("workflow.new_request")
async def new_request(request_schema: TopWorkflowRequestSchema):

    request_info = RequestInfo(workflow_name=request_schema.workflow_name)
    current_span = trace.get_current_span()

    # save the span attributes into a baggage that can be passed to underlying methods
    # baggage.set_baggage("workflow_name", request_info.workflow_name)

    with set_baggage_context(workflow_name=request_info.workflow_name):
        request_id = await request_service.new_request(request_info)
        current_span.set_attribute("workflow_name", request_info.workflow_name)
        current_span.set_attribute("request_id", request_id)

    return WorkflowResponseSchema(request_id = request_id,
                                     workflow_name=request_schema.workflow_name,
                                     request_status=RequestStatus.QUEUED.name)

@router.get(
    "/request/{request_id}",
    description="Get request details by the request ID",
    response_model=WorkflowResponseSchema,
)
async def get_request_details(request_id: str):

    request_info = await request_service.find_request_by_id(request_id)

    return WorkflowResponseSchema(
        request_id=request_id,
        workflow_name=request_info.workflow_name,
        request_status=request_info.request_status,
        start_time=request_info.start_time,
        end_time=request_info.end_time
    )
