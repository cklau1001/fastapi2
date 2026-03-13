"""
In SQLAlchemy, only database communication (connecting / executing a query) is async. The rest
creating an engine or session are synchronous)

"""
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,  AsyncSession

from db.db_driver import DBDriver

load_dotenv()

class PostgresAsync(DBDriver):

    def __init__(self):
        self._echo = True if os.getenv('ECHO', "true") in ["true", "True"] else False
        self._pool_size = os.getenv('POOL_SIZE', 10)
        self._pool_recycle = os.getenv('POOL_RECYCLE', 3600)
        self._connection_url = os.getenv('CONNECTION_URL')
        self._schema = os.getenv('DB_SCHEMA')
        self._engine = None
        self._sessionmaker = None

        self._initialize()


    def _initialize(self):

        if self._schema is None:
            raise ValueError(f"[_initialize]: Please provide DB_SCHEMA")

        if self._connection_url is None:
            raise ValueError(f"[_initialize]: Please provide CONNECTION_URL")

        if self._engine is None:
            self._engine = create_async_engine(
                self._connection_url,
                echo=self._echo,
                future=True,
                pool_size=self._pool_size,
                pool_recycle=self._pool_recycle,
                connect_args = {
                    "server_settings": {
                        "search_path": self._schema
                    }
                }
            )
            self._sessionmaker = async_sessionmaker(
                bind = self._engine,
                class_ = AsyncSession,
                expire_on_commit=False # Prevent lazy loading after commit, need to set for async driver
            )

    def create_engine(self):
        if self._engine is None:
            self._initialize()

        return self._engine

    def create_session(self):

        if self._sessionmaker is None:
            self._initialize()

        return self._sessionmaker


postgres_async_driver = PostgresAsync()