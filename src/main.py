"""

swagger: http://localhost:8001/docs

"""
from fastapi import FastAPI, Request, status
import uvicorn
from fastapi_pagination import add_pagination
from starlette.responses import JSONResponse

# change to another version by updating this import (e.g. v2)
from routers.v1.routes import heartbeatroute, workflow_request_route
from service.errorhandler import AppError
from otel.otel_config import initialize_tracer, fastapi_instrumentor

def create_app() -> FastAPI:

    app = FastAPI(
        title="FastAPI 2 endpoints",
        description="List of FastAPI 2 endpoints",
        version="0.1.0",
        root_path="/api/routers.v1"
    )

    add_pagination(app)
    app.include_router(heartbeatroute.router)
    app.include_router(workflow_request_route.router)

    initialize_tracer()
    fastapi_instrumentor.instrument_app(app)

    return app

app = create_app()
@app.exception_handler(AppError)
async def app_exception_handler(request: Request, exception: AppError):
    """
    Return the JSON error page for AppError

    :param request: a mandatory parameter used by fastapi, though it may not be used in this handler
    :param exception: The target AppError
    :return:
    """
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "message": exception.message
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request:Request, exception: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": str(exception)
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request:Request, exception: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": str(exception)
        }
    )

# main
if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, port=8001, log_level="debug")