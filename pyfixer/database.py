# -*- coding: utf-8 -*-
# The database settings for the fixer.py script

from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from settings import DB_URI

engine = create_engine(DB_URI, convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
Base = declarative_base()
Base.query = session.query_property()


class Rate(Base):
    """
    ORM DB rate class.
    """

    __tablename__ = 'rate'

    id = Column(Integer, primary_key=True)
    currency = Column(String(5))
    rate = Column(Integer)
    date = Column(DateTime)

    def __init__(self, currency, rate, date):
        self.currency = currency
        self.rate = rate
        self.date = date




