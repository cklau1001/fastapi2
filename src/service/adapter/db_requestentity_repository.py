"""
  database implementation of abstract class (RequestEntityRepository)
"""

import logging
from typing import List, Literal, get_args

from anyio.to_process import current_default_process_limiter
from sqlalchemy import select, update, func
from http import HTTPStatus

from .db_requestentity_mapper import RequestEntityMapper
from db.models import RequestEntity
from db.database import dbengine

from service.requestentity_repository import AsyncRequestEntityRepository
from service.logger import setup_logging
from service.requeststatus import RequestStatus
from service.utilhelper import datahelper
from service.errorhandler import AppError
from dto.requestinfo import RequestInfo
from otel.otel_config import tracer, trace, baggage, otelspan

setup_logging()
log = logging.getLogger(__name__)


RequestColumns = Literal[
    "workflow_name", "request_status", "start_time",
    "end_time", "remark", "payload", "created_by", "last_modified_by"
]

ALLOWED_UPDATE_COLUMNS = get_args(RequestColumns)

# VALID_ATTRS = {m.key for m in RequestEntity.__mapper__.column_attrs.keys() if hasattr(m, 'key')}

class AsyncDBRequestEntityRepository(AsyncRequestEntityRepository):

    def __init__(self):
        self._dbengine = dbengine

    @property
    def dbengine(self):
        return self._dbengine

    @tracer.start_as_current_span("db_requestentity_repo.new_request")
    # @otelspan("db_requestentity_repo.new_request")
    async def new_request(self, request_info: RequestInfo):

        if request_info is None:
            raise ValueError("[new_request]: request_info cannot be null")

        current_span = trace.get_current_span()
        current_span.set_attribute("request_id", str(baggage.get_baggage("request_id")))
        current_span.set_attribute("workflow_name", str(baggage.get_baggage("workflow_name")))

        request_entity = RequestEntityMapper.get_entity(request_info)
        async with self.dbengine.get_dbsession() as session:
            async with session.begin():  # start a transaction and commit if successful
                session.add(request_entity)

        log.info(f"[new_request]: request created, request_info={request_info}")

    async def find_request_by_id(self, request_id: str) -> RequestInfo:

        if request_id is None:
            raise ValueError("[find_request_by_id]: request_id cannot be None")

        stmt = select(RequestEntity).where(RequestEntity.request_id == request_id)

        async with self.dbengine.get_dbsession() as session:
            # need to execute stmt under await
            result = await session.execute(stmt)
            resultset = result.scalars().first()
            if resultset is None:
                raise AppError(message=f"No such request, request_id={request_id}", status_code=HTTPStatus.NOT_FOUND)
            request_info = RequestEntityMapper.get_dto(resultset)

        log.info(f"[find_request_by_id]: request_info={request_info}")
        return request_info

    async def find_requests_by_status(self, request_status: str) -> List[RequestInfo]:

        if request_status is None:
            raise ValueError("[find_requests_by_status]: request_status cannot be None")

        if request_status not in RequestStatus.__members__:
            raise ValueError(f"[find_requests_by_status]: invalid request_status={request_status}")

        stmt = select(RequestEntity).where(RequestEntity.request_status == RequestStatus[request_status])

        request_list = []
        async with self.dbengine.get_dbsession() as session:
            rows = await session.execute(stmt)
            results = rows.scalars().all()
            for r in results:
                request_info = RequestEntityMapper.get_dto(r)
                request_list.append(request_info)

        return request_list


    async def update_field(self, request_id: str, column: str, value: str):

        if request_id is None:
            raise ValueError("[update_field]: request_id cannot be None")

        if column is None:
            raise ValueError("[update_field]: column cannot be None")

        if column not in ALLOWED_UPDATE_COLUMNS:
            raise ValueError(f"[update_field]: Invalid column that is not part of RequestEntity, column={column}")

        converters = {
            "request_status": datahelper.str_to_requeststatus,
            "start_time": datahelper.str_to_datetime,
            "end_time": datahelper.str_to_datetime,
            "payload": datahelper.str_to_json
        }

        # Let ValueError except bubbles up
        if column in converters:
            value = converters[column](value)

        update_mapper = {
            column: value,
            "version": RequestEntity.version + 1,
            "last_modified_time": func.now()
        }

        stmt = (
            update(RequestEntity)
            .where(RequestEntity.request_id == request_id)
            .values(**update_mapper)
        )

        async with self.dbengine.get_dbsession() as session:
            async with session.begin():
                await session.execute(stmt)
                log.info(f"[update_field]: field updated, request_id={request_id}, column={column}, value={value}")


    async def update_request(self, request_info: RequestInfo, need_lock=False):
        """
        A method to update related RequestEntity from the RequestInfo. Suitable for updating multiple fields.

        :param request_info:
        :return:
        """

        if request_info is None:
            raise ValueError("[update_request]: request_info cannot be None")

        if request_info.request_id is None:
            raise ValueError("[update_request]: request_id of request_info cannot be None")

        stmt = select(RequestEntity).where(RequestEntity.request_id == request_info.request_id)

        if need_lock:
            stmt = stmt.with_for_update()

        async with (self.dbengine.get_dbsession() as session):
            async with session.begin():
                row = await session.execute(stmt)
                request_entity: RequestEntity = row.scalar_one_or_none()
                # request_entity: RequestEntity = session.scalar(stmt).first()

                if not request_entity:
                    raise AppError(message=f"[update_request]: invalid request_id for update, "
                                           f"request_id={request_info.request_id}",
                                   status_code=HTTPStatus.NOT_FOUND)

                request_entity.request_status = datahelper.str_to_requeststatus(request_info.request_status) \
                    if request_info.request_status else request_entity.request_status

                request_entity.start_time = request_info.start_time \
                    if request_info.start_time else request_entity.start_time

                request_entity.end_time = request_info.end_time if request_info.end_time else request_entity.end_time
                request_entity.remark = request_info.remark if request_info.remark else request_entity.remark
                request_entity.workflow_name = request_info.workflow_name \
                    if request_info.workflow_name else request_entity.workflow_name

                log.info(f"[update_request]: request updated, request_info={request_info}")
            # let commit to apply the change back to db


# singleton object
dbrequest_repo = AsyncDBRequestEntityRepository()
