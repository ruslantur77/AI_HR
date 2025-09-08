import asyncio
import io
import json
import logging
import re
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from uuid import UUID

import aiosmtplib
import docx2txt
import httpx
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from striprtf.striprtf import rtf_to_text

from config import config
from exceptions import NotFoundError
from llm import get_response, get_system_instruction
from resources.prompts import AUTO_SCREENING, INTERVIEW, QUESTIONS
from schemas import (
    AutoScreeningStatusEnum,
)
from services import InterviewQuestionsService, InterviewService, ResumeService

logger = logging.getLogger(__name__)


class ExtractText:
    def _from_image(self, file_obj: io.BytesIO) -> str:
        return pytesseract.image_to_string(Image.open(file_obj), lang="rus+eng")

    def _from_pdf(self, file_obj: io.BytesIO) -> str:
        text = "".join(
            (page.extract_text() or "") + "\n"
            for page in pdfplumber.open(file_obj).pages
        ).strip()

        if text:
            return text

        # OCR fallback
        images = convert_from_bytes(file_obj.getvalue())
        return "\n".join(
            f"--- Страница {i} ---\n{pytesseract.image_to_string(img, lang='rus+eng')}"
            for i, img in enumerate(images, 1)
        )

    def _from_docx(self, file_obj: io.BytesIO) -> str:
        with tempfile.NamedTemporaryFile(suffix=".docx") as tmp_file:
            tmp_file.write(file_obj.getbuffer())
            tmp_file.flush()
            return docx2txt.process(tmp_file.name)

    def _from_rtf(self, file_obj: io.BytesIO) -> str:
        return rtf_to_text(file_obj.read().decode("utf-8", errors="ignore"))

    _extractors = {
        ".jpg": _from_image,
        ".jpeg": _from_image,
        ".png": _from_image,
        ".bmp": _from_image,
        ".tiff": _from_image,
        ".pdf": _from_pdf,
        ".docx": _from_docx,
        ".rtf": _from_rtf,
    }

    def execute(self, file_path: Path) -> str:
        if not file_path.exists() or not file_path.is_file():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_path.suffix.lower()
        if ext not in self._extractors:
            logger.error(f"Unsupported file format: {ext}")
            raise ValueError(f"Unsupported file format: {ext}")

        with open(file_path, "rb") as f:
            file_obj = io.BytesIO(f.read())

        text = self._extractors[ext](self, file_obj)
        return re.sub(r"\n+", "\n", text).strip()


class ResumeAnalyzer:
    def __init__(self, API_KEY: str) -> None:
        self.URL = "https://openrouter.ai/api/v1/chat/completions"
        self.HEADERS = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

    def build_payload(self, requirements: str, resume_text: str) -> dict:

        user_prompt = f"ТРЕБОВАНИЯ:\n{requirements}\n\nРЕЗЮМЕ:\n{resume_text}"

        return {
            "model": "deepseek/deepseek-chat-v3.1",
            "messages": [
                {"role": "system", "content": AUTO_SCREENING},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 100,
            "temperature": 0.1,
        }

    async def execute(self, requirements: str, resume_text: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    self.URL,
                    headers=self.HEADERS,
                    json=self.build_payload(requirements, resume_text),
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"].strip()
                return content == "True"
        except httpx.RequestError as e:
            logger.error("API reques error", exc_info=e)
            raise ConnectionError(f"API reques error: {e}")
        except (KeyError, IndexError) as e:
            logger.error("Unexpected API response format", exc_info=e)
            raise ValueError("Unexpected API response format")


class EmailSendUseCase:
    SUBJECT = "Результат автоскрининга резюме"

    MESSAGES = {
        AutoScreeningStatusEnum.PASSED: (
            "Вы прошли этап автоскрининга! "
            "Для прохождения AI HR интервью перейдите по ссылке {link}"
        ),
        AutoScreeningStatusEnum.REJECTED: (
            "К сожалению, вы не прошли этап автоматического скрининга резюме."
        ),
    }

    def __init__(self, sender=config.EMAIL_SENDER, password=config.EMAIL_SENDER_PASS):
        self.sender = sender
        self.password = password

    async def _send(self, receiver: str, subject: str, body: str, html: bool = False):
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = self.sender, receiver, subject

        subtype = "html" if html else "plain"
        msg.attach(MIMEText(body, subtype))

        await aiosmtplib.send(
            msg,
            hostname="smtp.mail.ru",
            port=587,
            start_tls=True,
            username=self.sender,
            password=self.password,
        )

    async def execute(
        self, email: str, result: AutoScreeningStatusEnum, link: str | None = None
    ):
        body = self.MESSAGES.get(result)
        if not body:
            logger.error("Unexpected AutoScreening status")
            raise ValueError("Unexpected AutoScreening status")
        body = body.format(link=f'<a href="{link}">{link}</a>' or "")
        try:
            await self._send(email, self.SUBJECT, body, html=True)
        except Exception as e:
            logger.error("Error on sending letter", exc_info=e)


class ResumeProcessUseCase:
    def __init__(
        self,
        resume_service: ResumeService,
        interview_service: InterviewService,
        question_service: InterviewQuestionsService,
        api_key: str,
    ):
        self.resume_service = resume_service
        self.interview_service = interview_service
        self.question_service = question_service
        self.api_key = api_key

    async def execute(self, resume_id: UUID) -> None:
        try:
            resume = await self.resume_service.get(id=resume_id)
            if not resume:
                logger.error(f"Resume with id {resume_id} not found")
                raise NotFoundError(f"Resume with id {resume_id} not found")

            file_text = await asyncio.to_thread(
                ExtractText().execute, Path(resume.file_path)
            )

            analyzer = ResumeAnalyzer(self.api_key)
            passed = await analyzer.execute(resume.vacancy.description, file_text)

            if passed:
                status = AutoScreeningStatusEnum.PASSED
                interview = await self.interview_service.create(resume_id=resume.id)
                q = (
                    await get_response(
                        [get_system_instruction(QUESTIONS)],
                        f"""
                            На основе этих требований к вакансии:
                            {resume.vacancy.description}

                            И резюме этого кандидата:
                            {file_text}

                            Сгенерируй 5 конкретных вопросов для технического скринингового собеседования.
                            """,
                        max_tokens=5000,
                    )
                )[1]
                questions: list[str] = json.loads(q)
                welcome_text = await get_response(
                    [
                        get_system_instruction(
                            INTERVIEW.format(questions="\n".join(questions))
                        )
                    ],
                    "Здравствуйте!",
                )
                await self.question_service.add(
                    interview_id=interview.id,
                    questions=questions,
                    welcome_text=welcome_text[1],
                )

                link = f"{config.HOST}/?interview_id={interview.id}"
            else:
                status, link = AutoScreeningStatusEnum.REJECTED, None

            await self.resume_service.update_auto_screening_status(
                id=resume_id, status=status
            )

            email_uc = EmailSendUseCase()
            await email_uc.execute(resume.candidate.email, status, link)
        except Exception as e:
            logger.error(f"Error on processing resume {resume_id}", exc_info=e)
            await self.resume_service.update_auto_screening_status(
                resume_id, AutoScreeningStatusEnum.ERROR
            )
