import json
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models import InterviewQuestions


class InterviewQuestionsService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def add(
        self, interview_id: UUID, questions: list[str], welcome_text: str | None = None
    ) -> None:
        json_text = json.dumps(questions)
        async with self.session_factory() as session:
            result = await session.execute(
                select(InterviewQuestions).where(
                    InterviewQuestions.interview_id == interview_id
                )
            )
            iq = result.scalar_one_or_none()
            if iq:
                iq.text = json_text
                if welcome_text is not None:
                    iq.welcome_text = welcome_text
            else:
                iq = InterviewQuestions(
                    interview_id=interview_id,
                    text=json_text,
                    welcome_text=welcome_text or "",
                )
                session.add(iq)
            await session.commit()

    async def get_questions(self, interview_id: UUID) -> list[str]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(InterviewQuestions.text).where(
                    InterviewQuestions.interview_id == interview_id
                )
            )
            row = result.scalar_one_or_none()
            if row:
                return json.loads(row)
            return []

    async def get_welcome_text(self, interview_id: UUID) -> str:
        async with self.session_factory() as session:
            result = await session.execute(
                select(InterviewQuestions.welcome_text).where(
                    InterviewQuestions.interview_id == interview_id
                )
            )
            row = result.scalar_one_or_none()
            if row:
                return row
            return ""

    async def delete(self, interview_id: UUID) -> None:
        async with self.session_factory() as session:
            await session.execute(
                delete(InterviewQuestions).where(
                    InterviewQuestions.interview_id == interview_id
                )
            )
            await session.commit()
