'''
a utility class to perform conversion between DTO and Entity for request
'''
import logging
from typing import Literal

from dto.requestinfo import RequestInfo
from db.models import RequestEntity
from service.logger import setup_logging
from service.requeststatus import RequestStatus

setup_logging()
log = logging.getLogger(__name__)

IncomingDTO = Literal["RequestEntity"]   # Update this list to accept new supported type to generate DTO

class RequestEntityMapper:

    @staticmethod
    def get_entity(request_info: RequestInfo) -> RequestEntity | None:

        if request_info is None:
            log.warning("[get_entity]: request_info is None, return a None entity")
            return None

        request_entity = RequestEntity(
            request_id = request_info.request_id,
            workflow_name = request_info.workflow_name,
            request_status =  RequestStatus[request_info.request_status]
            if request_info.request_status else None,
            start_time = request_info.start_time,
            end_time = request_info.end_time,
            remark = request_info.remark
        )

        return request_entity

    @staticmethod
    def get_dto_from_entity(request_entity: RequestEntity) -> RequestInfo | None:

        if request_entity is None:
            log.error("[get_instance]: request_entity is None, no request_info can be generated from it.")
            return None

        request_info = RequestInfo(
            request_id = request_entity.request_id,
            workflow_name = request_entity.workflow_name,
            request_status = request_entity.request_status.name,
            start_time = request_entity.start_time,
            end_time = request_entity.end_time,
            remark = request_entity.remark
        )

        return request_info

    @staticmethod
    def get_dto(request: IncomingDTO) -> RequestInfo:
        '''
        Get RequestInfo from incoming object, currently supporting RequestEntity. It can be extended for other types in
        future

        :param request:
        :return:
        '''

        if request is None:
            raise ValueError("[get_dto]: request cannot be None")

        dto_mapper: dict = {
            "RequestEntity": RequestEntityMapper.get_dto_from_entity
        }

        log.debug(f"type(request) = {type(request).__name__}")
        if not type(request).__name__ in dto_mapper:
            raise ValueError(f"[get_dto]: un-supported incoming type for request, type={type(request).__name__}")


        return dto_mapper.get(type(request).__name__)(request)
