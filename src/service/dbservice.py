"""
This is a testing script. No relative import is allowed.

"""
import logging
import asyncio
from datetime import datetime, timezone

from db.database import dbengine
from db.models import Base
from service.logger import setup_logging
from dto.requestinfo import RequestInfo
from service.adapter.db_requestentity_repository import dbrequest_repo
from service.requestservice import request_service


setup_logging()
log = logging.getLogger(__name__)


async def async_create_tables():

    async with dbengine.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    log.info(f"[create_tables]: tables created")

async def testdb():


    request_info = RequestInfo(
        request_id = "123-123",
        workflow_name="buyTicket"
    )

    new_request_info = RequestInfo(
        request_id = request_info.request_id,
        request_status = "EXECUTING",
        remark = "added a remark"
    )

    # await dbrequest_repo.new_request(request_info)
    # await dbrequest_repo.find_request_by_id(request_info.request_id)
    result = await dbrequest_repo.find_request_by_status("QUEUED")

    # await dbrequest_repo.update_field(request_info.request_id, "start_time", datetime.now(timezone.utc).isoformat() )
    await dbrequest_repo.update_request(new_request_info, need_lock=True)

    log.info(f"[testdb]: result={result}")

async def test_requestservice():

    request_info = RequestInfo(
        request_id = "123-123",
        workflow_name="buyTicket"
    )

    # 491fff6b-c4ad-45c1-a72b-a1545f8ee9d5
    # await request_service.new_request(request_info)
    # await request_service.find_request_by_id("491fff6b-c4ad-45c1-a72b-a1545f8ee9d5")
    # result = await request_service.find_requests_by_status("QUEUED")
    # log.info(f"result={result}")

    await request_service.update_remark("123-123", "new remark")

# main

if __name__ == "__main__":

    # run an async call in a sync context
    # asyncio.run() can only be triggered once in a program.
    # so, need to wrap all async function in a top level wrapper for it to trigger
    #
    # asyncio.run(async_create_tables())
    #
    # log.info("Table created")

    # asyncio.run(testdb())
    asyncio.run(test_requestservice())
