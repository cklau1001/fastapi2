import os
from dotenv import load_dotenv
from contextlib import contextmanager, asynccontextmanager

from .dbdriver_factory import DBDriverFactory

load_dotenv()
DATABASE_TYPE = os.getenv('DATABASE_TYPE')

class DBEngine:

    def __init__(self):
        self._engine = None
        self._sessionmaker = None

        self._initialize()

    def _initialize(self, database=DATABASE_TYPE):

        dbdriver = DBDriverFactory.get_instance(database)
        self._engine = dbdriver.create_engine()
        self._sessionmaker = dbdriver.create_session()

    @property
    def engine(self):

        if self._engine is None:
            self._initialize()
        return self._engine

    @contextmanager  # ensure that each thread has its own isolated session
    def get_sync_dbsession(self):

        with self._sessionmaker() as session:
            try:
                yield session
                # session.commit()   # let caller determine if a transaction is needed by session.begin()
            except Exception:
                session.rollback()
                raise

    @asynccontextmanager
    async def get_async_dbsession(self):

        async with self._sessionmaker() as session:
            try:
                yield session
                # await session.commit()  # let caller determine if a transaction is needed by session.begin()
            except Exception:
                await session.rollback()
                raise
            # async with handle session close()

    # return the callable context manager by using a normal method
    def get_dbsession(self):
        if "async" in DATABASE_TYPE:
            return self.get_async_dbsession()  # return the generator object

        return self.get_sync_dbsession()


    #
    # The following shows how to trigger the get_dbsession() in both sync and async scenarios
    #
    def use_sync_session(self):

        # if DATABASE driver is sync
        with self.get_dbsession() as session:
            pass

    async def use_async_session(self):

        # if DATABASE driver is async, still need to know which driver it is using
        # color problem
        #
        async with dbengine.get_dbsession() as session:
            pass

dbengine = DBEngine()

