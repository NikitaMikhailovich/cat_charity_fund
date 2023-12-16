from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_charity_closed_before_update,
                                check_charity_invested_delete,
                                check_charity_project_exists,
                                check_full_amount_update, check_name_duplicate)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.donation_process import donation_process

router = APIRouter()


@router.get('/',
            response_model=list[CharityProjectDB],
            response_model_exclude_none=True,
            )
async def get_all_charity_project(
    session: AsyncSession = Depends(get_async_session),
):
    all_projects = await charity_crud.get_multi(session)
    return all_projects


@router.post('/',
             response_model=CharityProjectDB,
             response_model_exclude_none=True,
             dependencies=[Depends(current_superuser)],
             )
async def create_new_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""

    await check_name_duplicate(charity_project.name, session)
    new_charity = await charity_crud.create(charity_project, session)
    await donation_process(new_charity, session)
    await session.refresh(new_charity)
    return new_charity


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
        charity_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):

    charity_project = await check_charity_project_exists(
        charity_id, session
    )

    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)

    await check_charity_closed_before_update(charity_id, session)
    await check_full_amount_update(charity_project, obj_in.full_amount)
    charity_project = await charity_crud.update(
        charity_project, obj_in, session
    )
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
        charity_id: int,
        session: AsyncSession = Depends(get_async_session),
):

    charity_project = await check_charity_project_exists(
        charity_id, session
    )
    await check_charity_invested_delete(charity_id, session)
    charity_project = await charity_crud.remove(charity_project, session)
    return charity_project