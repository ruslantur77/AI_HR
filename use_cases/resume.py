import asyncio
import io
import re
import tempfile
from pathlib import Path
from uuid import UUID

import docx2txt
import httpx
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from striprtf.striprtf import rtf_to_text

from exceptions import NotFoundError
from schemas import AutoScreeningStatusEnum
from services import ResumeService
from services.vacancy_service import VacancyService


class ExtractText:
    def extract_text_from_image(self, file_obj: io.BytesIO) -> str:
        img = Image.open(file_obj)
        return pytesseract.image_to_string(img, lang="rus+eng")

    def extract_text_from_pdf(self, file_obj: io.BytesIO) -> str:
        text = ""
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    text += txt + "\n"

        if text.strip():
            return text

        images = convert_from_bytes(file_obj.getvalue())
        ocr_text = []
        for i, image in enumerate(images, 1):
            ocr_text.append(
                f"\n--- Страница {i} ---\n{pytesseract.image_to_string(image, lang='rus+eng')}"
            )
        return "".join(ocr_text)

    def extract_text_from_docx(self, file_obj: io.BytesIO) -> str:
        with tempfile.NamedTemporaryFile(suffix=".docx") as tmp_file:
            tmp_file.write(file_obj.getbuffer())
            tmp_file.flush()
            text = docx2txt.process(tmp_file.name)
        return text

    def extract_text_from_rtf(self, file_obj: io.BytesIO) -> str:
        content = file_obj.read().decode("utf-8", errors="ignore")
        return rtf_to_text(content)

    def extract_text(self, file_obj: io.BytesIO, ext: str) -> str:
        ext = ext.lower()
        if ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
            return self.extract_text_from_image(file_obj)
        elif ext == ".pdf":
            return self.extract_text_from_pdf(file_obj)
        elif ext == ".docx":
            return self.extract_text_from_docx(file_obj)
        elif ext == ".rtf":
            return self.extract_text_from_rtf(file_obj)
        else:
            raise ValueError(f"Неподдерживаемый формат: {ext}")

    def execute(self, file_path: Path) -> str:
        ext = file_path.suffix.lower()
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        with open(file_path, "rb") as f:
            file_obj = io.BytesIO(f.read())

        return re.sub(r"\n+", "\n", self.extract_text(file_obj, ext))


class ResumeAnalyzer:
    def __init__(self, API_KEY: str) -> None:
        self.URL = "https://openrouter.ai/api/v1/chat/completions"
        self.HEADERS = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

    def build_payload(self, requirements: str, resume_text: str) -> dict:
        system_prompt = """
Ты — AI-ассистент рекрутера. Твоя задача — объективно оценить, соответствует ли резюме кандидата предоставленным \
требованиям вакансии.
Инструкция:
 Внимательно изучи ТРЕБОВАНИЯ к вакансии и РЕЗЮМЕ кандидата.
 Проведи детальный анализ по ключевым критериям: опыт работы, ключевые навыки (Hard Skills), знание методологий,\
    инструментов и технологий, релевантный опыт.
 Основное внимание уделяй содержанию, а не форме составления резюме.
 Сравни каждый ключевой пункт из требований с тем, что указано в резюме.
Критерий для возврата True (Принять):
Кандидат имеет подтвержденный опыт работы на аналогичной позиции, соответствующий требуемому уровню.
В резюме четко видны и совпадают КЛЮЧЕВЫЕ навыки из требований.
Резюме демонстрирует релевантный опыт решения задач, указанных в обязанностях вакансии.
Критерий для возврата False (Отклонить):
Опыт работы отсутствует или значительно меньше требуемого.
В резюме отсутствует большинство ключевых hard skills из требований.
Кандидат является специалистом из смежной или другой области без подтвержденного релевантного опыта.
Важно:
Не отклоняй кандидата только из-за отсутствия части желательных (Nice to have) навыков.
Если ключевые требования совпадают, а второстепенные навыки или уровень английского не указаны — это не повод для False.
Твой ответ должен быть строго одним словом: `True` или `False`. Никаких пояснений, комментариев или форматирования в \
    ответе быть не должно.
"""
        user_prompt = f"ТРЕБОВАНИЯ:\n{requirements}\n\nРЕЗЮМЕ:\n{resume_text}"

        return {
            "model": "deepseek/deepseek-chat-v3.1",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
        }

    async def execute(self, requirements: str, resume_text: str) -> bool:
        payload = self.build_payload(requirements, resume_text)
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    self.URL, headers=self.HEADERS, json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip() == "True"
        except httpx.RequestError as e:
            raise ConnectionError(f"Ошибка запроса к API: {e}")
        except (KeyError, IndexError):
            raise ValueError("Неожиданный формат ответа API")


class ResumeProcessUseCase:

    def __init__(
        self,
        vacancy_service: VacancyService,
        resume_service: ResumeService,
        API_KEY: str,
    ) -> None:
        self.vacancy_service = vacancy_service
        self.resume_service = resume_service
        self.API_KEY = API_KEY

    async def execute(self, vacancy_id: UUID, resume_id: UUID) -> None:
        resume = await self.resume_service.get(id=resume_id)
        if not resume:
            raise NotFoundError(f"Resume with id {resume_id} not found")
        file_path = Path(resume.file_path)
        extract_uc = ExtractText()

        text = await asyncio.to_thread(extract_uc.execute, file_path=file_path)

        vacancy = await self.vacancy_service.get(vacancy_id)
        if not vacancy:
            raise NotFoundError(f"Vacancy with id {vacancy_id} not found")
        requirements = vacancy.description

        analyze_uc = ResumeAnalyzer(API_KEY=self.API_KEY)
        res = await analyze_uc.execute(requirements=requirements, resume_text=text)
        if res:
            new_status = AutoScreeningStatusEnum.PASSED
        else:
            new_status = AutoScreeningStatusEnum.REJECTED
        await self.resume_service.update_auto_screening_status(
            id=resume_id, status=new_status
        )
