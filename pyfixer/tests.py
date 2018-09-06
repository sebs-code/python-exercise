# -*- coding: utf-8 -*-
# fixer.py tests file

from unittest.mock import patch
from datetime import datetime

import pytest
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from fixer import Fixer
from settings import API_HOME, API_KEY, BASE_CURRENCY, CURRENCIES

# Test db engine
engine = create_engine('sqlite://', convert_unicode=True)
test_session = scoped_session(sessionmaker(autocommit=False,
                                           autoflush=False,
                                           bind=engine))
Base = declarative_base()

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

Base.metadata.create_all(engine)


@patch('fixer.Fixer')
def test_call_endpoint(MockFixer):
    fixer = MockFixer()

    fixer.call_endpoint.return_value = [
        {
            "success": True,
            "timestamp": 1519296206,
            "base": "EUR",
            "date": "2018-09-06",
            "rates": {
                "AUD": 1.566015,
            }
        }
    ]

    response = fixer.call_endpoint()

    assert response is not None
    assert  type(response[0]) == dict


def test_create_update_rate():
    fixer = Fixer(None , None, None, None, dbsession=test_session)
    fixer.create_or_update_rate(datetime.now(), 'USD', '2.566015')
    query = test_session.query(Rate).first()

    assert query.currency == 'USD'
    assert query.rate == 2.566015

