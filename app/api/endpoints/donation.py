from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user import current_superuser, current_user
from app.models import User

from app.core.db import get_async_session
from app.crud.donation import donation_crud
from app.schemas.donation import (
    DonationCreate, DonationGet, DonationDB
)
from app.services.donation_process import donation_process

router = APIRouter()


@router.post(
    '/',
    response_model=DonationGet,
    response_model_exclude_none=True
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):

    new_donation = await donation_crud.create(
        donation, session, user
    )
    await donation_process(new_donation, session)
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/',
    response_model=list[DonationDB],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def get_all_donation(
        session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    donations = await donation_crud.get_multi(session)
    return donations


@router.get(
    '/my',
    response_model=list[DonationGet],
    response_model_exclude={'user_id'},
)
async def get_my_donation(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    donation = await donation_crud.get_by_user(
        session=session, user=user
    )
    return donation
