from __future__ import annotations

import uuid
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, TypeDecorator
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from schemas import (
    AutoScreeningStatusEnum,
    InterviewResultEnum,
    UserRoleEnum,
    VacancyStatusEnum,
)


class Base(DeclarativeBase):
    pass


class UUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(str(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(value)


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum, name="user_role", native_enum=True),
        default=UserRoleEnum.RECRUITER,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    def __init__(self, email: str, password_hash: str):
        self.email = email
        self.password_hash = password_hash


class RefreshTokensOrm(Base):
    __tablename__ = "refresh_tokens"
    jti: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(), ForeignKey("users.id", ondelete="CASCADE")
    )
    token_hash: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __init__(
        self,
        jti: uuid.UUID,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ):
        self.jti = jti
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at


class VacancyOrm(Base):
    __tablename__ = "vacancies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[VacancyStatusEnum] = mapped_column(
        Enum(VacancyStatusEnum, name="vacancy_status", native_enum=True),
        default=VacancyStatusEnum.OPEN,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    resumes: Mapped[list["ResumeOrm"]] = relationship(
        back_populates="vacancy",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description


class CandidateOrm(Base):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    resume: Mapped["ResumeOrm"] = relationship(
        back_populates="candidate",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(self, full_name: str, email: str):
        self.full_name = full_name
        self.email = email


class ResumeOrm(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(), ForeignKey("candidates.id"), nullable=False, unique=False
    )
    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(), ForeignKey("vacancies.id"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    auto_screening_status: Mapped[AutoScreeningStatusEnum] = mapped_column(
        Enum(AutoScreeningStatusEnum, name="auto_screening_status", native_enum=True),
        default=AutoScreeningStatusEnum.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    candidate: Mapped["CandidateOrm"] = relationship(
        back_populates="resume",
        lazy="selectin",
    )
    vacancy: Mapped["VacancyOrm"] = relationship(
        back_populates="resumes",
        lazy="selectin",
    )
    interview: Mapped["InterviewOrm"] = relationship(
        back_populates="resume",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(self, candidate_id: uuid.UUID, vacancy_id: uuid.UUID, file_path: str):
        self.candidate_id = candidate_id
        self.vacancy_id = vacancy_id
        self.file_path = file_path


class InterviewOrm(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(), ForeignKey("resumes.id"), nullable=False, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    passed_at: Mapped[datetime] = mapped_column(nullable=True)
    result: Mapped[InterviewResultEnum] = mapped_column(
        Enum(InterviewResultEnum, name="interview_result", native_enum=True),
        default=InterviewResultEnum.PENDING,
        nullable=False,
    )
    feedback_hr: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback_candidate: Mapped[str | None] = mapped_column(Text, nullable=True)

    resume: Mapped["ResumeOrm"] = relationship(
        back_populates="interview",
        lazy="selectin",
    )

    def __init__(
        self,
        resume_id: uuid.UUID,
        result: InterviewResultEnum = InterviewResultEnum.PENDING,
        feedback_hr: str | None = None,
        feedback_candidate: str | None = None,
    ):
        self.resume_id = resume_id
        self.result = result
        self.feedback_hr = feedback_hr
        self.feedback_candidate = feedback_candidate


class InterviewQuestions(Base):
    __tablename__ = "interview_questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(
        UUID(), ForeignKey("interviews.id"), nullable=False, unique=True
    )
    text: Mapped[str] = mapped_column(String)
    welcome_text: Mapped[str] = mapped_column(String)
