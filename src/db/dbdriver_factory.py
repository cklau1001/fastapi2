"""
Simple factory to return target db driver

"""
from .db_driver import DBDriver
from .adapter.postgres_async import postgres_async_driver

class DBDriverFactory:

    _registry: dict[str, DBDriver] = {
        "postgres_async": postgres_async_driver
    }

    @classmethod
    def get_instance(cls, database_type: str) -> DBDriver:

        if database_type not in cls._registry:
            raise ValueError(f"[get_instance]: Un-supported driver, database_type=${database_type}")

        return cls._registry.get(database_type)

