"""
The service class providing business logic

"""
import os
import uuid
import logging
from dotenv import load_dotenv

from dto.requestinfo import RequestInfo
from otel.otel_config import tracer, trace, baggage, set_baggage_context, otelspan
from .requeststatus import RequestStatus
from .requestentity_repository import AsyncRequestEntityRepository
from .repository_factory import RepositoryFactory
from .logger import setup_logging


setup_logging()
load_dotenv()

log = logging.getLogger(__name__)

class RequestService:

    def __init__(self):
        """
            use composition to store the actual repository implementation class
            i.e. command pattern, and this class is the invoker

        """

        self._requestrepo: AsyncRequestEntityRepository = (
            RepositoryFactory.get_request_repository(os.getenv("DATABASE_TYPE")))

    @property
    def requestrepo(self) -> AsyncRequestEntityRepository:
        return self._requestrepo

    @tracer.start_as_current_span("requestservice.new_request")
    # @otelspan("requestservice.new_request")
    async def new_request(self, request_info: RequestInfo) -> str:

        current_span = trace.get_current_span()

        if request_info is None:
            raise ValueError("[new_request]: request_info cannot be None")

        request_info.request_id = str(uuid.uuid4())
        request_info.request_status = RequestStatus.QUEUED.name

        with set_baggage_context(request_id=request_info.request_id):

            current_span.set_attribute("request_id", request_info.request_id)
            current_span.set_attribute("workflow_name", str(baggage.get_baggage("workflow_name")))

            await self.requestrepo.new_request(request_info)
            log.info(f"[new_request]: request created, request_id={request_info.request_id}")

        return request_info.request_id

    async def find_request_by_id(self, request_id: str) -> RequestInfo:

        return await self.requestrepo.find_request_by_id(request_id)

    async def find_requests_by_status(self, request_status: str) -> list[RequestInfo]:

        return await self.requestrepo.find_requests_by_status(request_status)

    async def update_remark(self, request_id: str, remark: str):

        if request_id is None:
            raise ValueError("[update_remark]: request_id is None")

        if remark is None or not remark:
            raise ValueError("[update_remark]: remark is empty")

        await self.requestrepo.update_field(request_id, "remark", remark)

request_service = RequestService()
