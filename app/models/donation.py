from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.basemodel_charity import BaseModelCharity


class Donation(BaseModelCharity):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)