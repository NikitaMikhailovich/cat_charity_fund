from datetime import datetime
from typing import List, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import false

from app.models import CharityProject, Donation


async def donation_process(
    obj_in: Union[CharityProject, Donation],
    session: AsyncSession
) -> Union[CharityProject, Donation]:
    model_in_process = (
        CharityProject if isinstance(obj_in, Donation) else Donation
    )

    available_objects = await get_obj_not_fully_invested(
        model_in_process, session
    )
    available_amount = obj_in.full_amount
    # if available_objects:
    #     for obj in available_objects:
    #         need_amount = obj.full_amount - obj.invested_amount

    #         if need_amount < available_amount:
    #             invest = need_amount
    #         else:
    #             invest = available_amount

    #         obj_in.invested_amount += invest
    #         available_amount -= invest
    #         obj.invested_amount += invest

    #         if obj.full_amount == obj.invested_amount:
    #             await close_fully_invested_object(obj)

    #         if available_amount == 0:
    #             await close_fully_invested_object(obj_in)
    #             break

    #     await session.commit()
    # return obj_in
    if not available_objects:
        return obj_in
    for obj in available_objects:
        need_amount = obj.full_amount - obj.invested_amount

        if need_amount < available_amount:
            invest = need_amount
        else:
            invest = available_amount

        obj_in.invested_amount += invest
        available_amount -= invest
        obj.invested_amount += invest

        if obj.full_amount == obj.invested_amount:
            await close_fully_invested_object(obj)

        if available_amount == 0:
            await close_fully_invested_object(obj_in)
            break

    await session.commit()
    return obj_in


async def get_obj_not_fully_invested(
    obj_in: Union[CharityProject, Donation],
    session: AsyncSession
) -> List[Union[CharityProject, Donation]]:
    objects = await session.execute(
        select(obj_in)
        .where(obj_in.fully_invested == false())
        .order_by(
            obj_in.create_date
        )
    )
    return objects.scalars().all()


async def close_fully_invested_object(
    obj_in: Union[CharityProject, Donation],
) -> None:
    obj_in.fully_invested = True
    obj_in.close_date = datetime.now()