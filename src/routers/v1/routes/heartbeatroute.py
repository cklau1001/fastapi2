from fastapi import APIRouter, Request, Response, status, Depends
from datetime import datetime, timezone
from typing import Annotated

from otel.otel_config import tracer, trace
from schemas.heartbeatschema import HeartBeatResponse


class DummyClass:
    """
    A test on dependency injection for this route

    """
    def __init__(self, name):
        self._name = name

router = APIRouter(
    prefix = "/heartbeat",
    tags = ["heartbeat"],
    responses = {
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# define dependency function below
def get_dummy(request: Request) -> DummyClass:
    return DummyClass(f"123-{request.client.host}-{request.client.port}")

# annotate the function, that can be used in route method
DummyClassDI = Annotated[DummyClass, Depends(get_dummy)]

# define route below

@router.get("/",
            summary="Heartbeat",
            description="Get a heartbeat",
            response_model=HeartBeatResponse)
def pulse(request: Request, response: Response):

    with tracer.start_as_current_span("heartbeat.pulse") as span:
        span.set_attribute("method", "pulse")
        span.set_attribute("uuid", "123")

        response.status_code = status.HTTP_200_OK
        return HeartBeatResponse(
            time=datetime.now(timezone.utc),
            IP=request.headers.get("X-Forwarded-For", request.client.host),
            message="I am alive"
        )


@router.get("/DI",
            summary="Heartbeat",
            description="Get a heartbeat (DI)",
            response_model=HeartBeatResponse)
@tracer.start_as_current_span("heartbeat.pulseDI")  # need to place the @tracer before @router
def pulseDI(request: Request, response: Response, dummy: DummyClass = Depends(get_dummy)):
    """
    An example of dependency injection that just pass a function reference to this method

    :param request:
    :param response:
    :param dummy:
    :return:
    """

    current_span = trace.get_current_span()
    current_span.set_attribute("method", "pulseDI")
    current_span.set_attribute("uuid", "456-456")

    response.status_code = status.HTTP_200_OK
    return HeartBeatResponse(
        time=datetime.now(timezone.utc),
        IP=request.headers.get("X-Forwarded-For", request.client.host),
        message=f"Dummy object is {dummy._name}"
    )


@router.get("/DI2",
            summary="Heartbeat",
            description="Get a heartbeat (DI)",
            response_model=HeartBeatResponse)
@tracer.start_as_current_span("heartbeat.pulseDI2")
def pulseDI2(request: Request, response: Response, dummy: DummyClassDI):
    """
    a short-hand version to inject dependency using Annotated type

    :param request:
    :param response:
    :param dummy:
    :return:
    """

    current_span = trace.get_current_span()
    current_span.set_attribute("method", "pulseDI2")
    current_span.set_attribute("uuid", "456-456-2")

    response.status_code = status.HTTP_200_OK
    return HeartBeatResponse(
        time=datetime.now(timezone.utc),
        IP=request.headers.get("X-Forwarded-For", request.client.host),
        message=f"Dummy object is {dummy._name}"
    )
