import enum
import logging

from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum, JSON, func, Index, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from service.requeststatus import RequestStatus
from service.taskstatus import TaskStatus
from service.logger import setup_logging

setup_logging()
log = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

class RequestEntity(Base):
    __tablename__ = "fa_request_entity"
    __table_args__ = (
        Index("idx_request_fa_requeststatus", "REQUEST_STATUS"),
    )

    request_id: Mapped[str] = mapped_column(
        String(255),
        primary_key = True,
        name = "REQUEST_ID"
    )

    workflow_name: Mapped[str] = mapped_column(
        String(255),
        name = "WORKFLOW_NAME"
    )

    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        name = "START_TIME",
        server_default = func.now()
    )

    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        name = "END_TIME",
    )

    request_status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, native_enum = False), # use enum string to store the value, @EnumType.STRING
        default = RequestStatus.QUEUED,
        name = "REQUEST_STATUS"
    )

    payload: Mapped[Optional[dict]] = mapped_column(
        JSON,
        name = "PAYLOAD"
    )

    remark: Mapped[Optional[str]] = mapped_column(
        String(2000),
        name = "REMARK"
    )

    # for audit trail
    created_by: Mapped[Optional[str]] = mapped_column(
        String(32),
        name = "CREATED_BY"
    )

    created_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        name = "CREATED_TIME",
        server_default = func.now()
    )

    last_modified_by: Mapped[Optional[str]] = mapped_column(
        String(32),
        name = "LAST_MODIFIED_BY"
    )

    last_modified_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        name = "LAST_MODIFIED_TIME",
        server_default = func.now(),
        onupdate = func.now(),
    )

    version: Mapped[int] = mapped_column(
        Integer,
        name = "VERSION"
    )

    # one-to-many relationship
    tasks: Mapped[list[TaskEntity]] = relationship(
        back_populates = "request",
        cascade = "all, delete-orphan"
    )


    __mapper_args__ = {
        "version_id_col": version
    }

class TaskEntity(Base):

    __tablename__ = "fa_task_entity"
    __table_args__ = (
        Index("idx_task_fa_taskstatus", "TASK_STATUS"),
    )

    task_id: Mapped[str] = mapped_column(
        String(255),
        primary_key = True,
        name = "TASK_ID"
    )

    step_id: Mapped[str] = mapped_column(
        String(255),
        name = "STEP_ID"
    )

    task_name: Mapped[str] = mapped_column(
        String(255),
        name = "TASK_NAME"
    )

    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        name = "START_TIME",
        server_default = func.now()
    )

    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        name = "end_time"
    )

    task_status: Mapped[Optional[TaskStatus]] = mapped_column(
        Enum(TaskStatus, native_enum = False),
        name = "TASK_STATUS",
        default = TaskStatus.QUEUED
    )

    next_retry_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        name = "NEXT_RETRY_AT"
    )

    retry_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        name = "RETRY_COUNT",
        default = 0
    )

    context: Mapped[Optional[dict]] = mapped_column(
        JSON,
        name = "CONTEXT"
    )

    remark: Mapped[Optional[str]] = mapped_column(
        String(2000),
        name = "REMARK"
    )

    # for audit trail
    created_by: Mapped[Optional[str]] = mapped_column(
        String(32),
        name = "CREATED_BY"
    )

    created_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        name = "CREATED_TIME",
        server_default = func.now()
    )

    last_modified_by: Mapped[Optional[str]] = mapped_column(
        String(32),
        name = "LAST_MODIFIED_BY"
    )

    last_modified_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        name = "LAST_MODIFIED_TIME",
        server_default = func.now(),
        onupdate = func.now(),
    )

    version: Mapped[int] = mapped_column(
        Integer,
        name = "VERSION"
    )

    # many-to-one, set up foreign key
    request_id: Mapped[str] = mapped_column(
        ForeignKey("fa_request_entity.REQUEST_ID")
    )

    request: Mapped["RequestEntity"] = relationship(
        back_populates = "tasks"
    )

    __mapper_args__ = {
        "version_id_col": version
    }

