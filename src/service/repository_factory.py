
from .requestentity_repository import AsyncRequestEntityRepository
from .adapter.db_requestentity_repository import dbrequest_repo

class RepositoryFactory:

    # For request entity repository
    _request_registry = {
        "postgres_async": dbrequest_repo
    }

    # For task entity repository
    _task_registry = {
        "postgres_async": None
    }

    @classmethod
    def get_request_repository(cls, driver) -> AsyncRequestEntityRepository:

        if driver in cls._request_registry:
            return cls._request_registry[driver]

        raise ValueError(f"[get_request_repository]: un-supported driver, driver={driver}")
    