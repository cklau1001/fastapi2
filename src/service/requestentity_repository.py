import abc

from dto.requestinfo import RequestInfo

class AsyncRequestEntityRepository(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def new_request(self, request_info: RequestInfo):
        raise NotImplementedError

    @abc.abstractmethod
    async def find_request_by_id(self, request_id: str) -> RequestInfo:
        raise NotImplementedError

    @abc.abstractmethod
    async def find_requests_by_status(self, request_status: str) -> list[RequestInfo]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_field(self, request_id: str, column: str, value: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def update_request(self, request_info: RequestInfo, need_lock=False):
        raise NotImplementedError
