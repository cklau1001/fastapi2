"""
A util helper for cross-domain usage. Each class is created for specific purpose, instead of putting all utility
functions into one single class.

"""

import json
from datetime import datetime

from service.requeststatus import RequestStatus

class DataHelper:

    def str_to_int(self, value: str) -> int | None:

        if value is None:
            return None
        return int(value)

    def str_to_datetime(self, value: str) -> datetime | None:

        if value is None:
            return None

        # Need to take out timezone info for the timestamp column in Postgres by replace()
        # when using asyncpg. No issue for sync driver (pscopg2)
        return datetime.fromisoformat(value).replace(tzinfo=None)

    def str_to_requeststatus(self, value: str) -> RequestStatus | None:

        if value is None:
            return None

        if value not in RequestStatus.__members__:
            raise ValueError(f"[to_requeststatus]: invalid request status, value={value}")

        return RequestStatus[value]

    def str_to_json(self, value: str) -> dict | None:

        if value is None:
            return None

        return json.loads(value)

datahelper = DataHelper()
