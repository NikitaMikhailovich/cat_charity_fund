from sqlalchemy import Column, String, Text

from app.models.basemodel_charity import BaseModelCharity


class CharityProject(BaseModelCharity):

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)