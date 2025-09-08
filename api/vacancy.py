from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_access_token_data, get_vacancy_service
from schemas import AccesTokenData, VacancyCreate, VacancyResponse
from services import VacancyService

router = APIRouter(prefix="/api/vacancy", tags=["vacancy"])


@router.post("/", response_model=VacancyResponse)
async def create_vacancy(
    vacancy_data: VacancyCreate,
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    vacancy_service: VacancyService = Depends(get_vacancy_service),
) -> VacancyResponse:
    res = await vacancy_service.create(
        title=vacancy_data.title, description=vacancy_data.description
    )
    return res


@router.get("/", response_model=list[VacancyResponse])
async def get_all_vacancies(
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    vacancy_service: VacancyService = Depends(get_vacancy_service),
) -> list[VacancyResponse]:
    res = await vacancy_service.get_all()
    return res


@router.get("/{vacancy_id}", response_model=VacancyResponse)
async def get_vacancy(
    vacancy_id: UUID,
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    vacancy_service: VacancyService = Depends(get_vacancy_service),
) -> VacancyResponse:
    res = await vacancy_service.get(id=vacancy_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found",
        )
    return res
