from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_crud
from app.models import CharityProject
# from app.crud.reservation import reservation_crud


async def check_name_duplicate(
        charity_name: str,
        session: AsyncSession,
) -> None:
    room_id = await charity_crud.get_project_id_by_name(charity_name, session)
    if room_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exists(
        charity_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_crud.get(charity_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=404,
            detail='Объект не найден!'
        )
    return charity_project


async def check_charity_closed_before_update(
        charity_id: int,
        session: AsyncSession,
):
    charity_project = await charity_crud.get(
        obj_id=charity_id, session=session
    )
    if charity_project.fully_invested is True:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать'
        )
    return charity_project


async def check_full_amount_update(
        charity_project,
        new_full_amount,
):
    if new_full_amount:
        if new_full_amount < charity_project.invested_amount:
            raise HTTPException(
                status_code=400,
                detail='Нельзя установить требуемую сумму меньше вложенной'
            )
    return charity_project


async def check_charity_invested_delete(
        charity_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_crud.get(
        obj_id=charity_id, session=session
    )
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail='Нельзя удалить проект, в который вложены средства'
        )
    return charity_project