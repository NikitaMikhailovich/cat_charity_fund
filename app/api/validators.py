from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_crud
from app.models import CharityProject
from http import HTTPStatus


async def check_name_duplicate(
        charity_name: str,
        session: AsyncSession,
) -> None:
    room_id = await charity_crud.get_project_id_by_name(charity_name, session)
    if room_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exists(
        charity_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_crud.get(charity_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
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
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )


async def check_full_amount_update(
        charity_project,
        new_full_amount,
):
    if new_full_amount:
        if new_full_amount < charity_project.invested_amount:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Нельзя установить требуемую сумму меньше вложенной'
            )


async def check_charity_invested_delete(
        charity_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_crud.get(
        obj_id=charity_id, session=session
    )
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )