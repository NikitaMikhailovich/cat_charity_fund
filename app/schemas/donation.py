from typing import Optional

from pydantic import BaseModel, Field, PositiveInt, Extra
from datetime import datetime


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationCreate(DonationBase):
    pass


class DonationGet(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationDB(DonationGet):
    user_id: int
    invested_amount: int = Field(0)
    fully_invested: bool = Field(False)
    close_date: Optional[datetime]