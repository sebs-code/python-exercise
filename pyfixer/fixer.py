# -*- coding: utf-8 -*-
# The main fixer.py script

import logging
import urllib.request, json
from datetime import datetime, timedelta

from settings import API_HOME, API_KEY, BASE_CURRENCY, CURRENCIES
from database import session, Rate


class Fixer(object):
    """
    The main class, used to query the fixer API, store data and check
    30 data history of currencies provided.
    """

    def __init__(self, api_home, api_key, base_currency, currencies,
                 dbsession=session):

        # API settings
        self.api = api_home
        self.api_key= api_key
        self.base_currency = base_currency
        self.currencies = currencies
        self.session = dbsession

        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)


    def call_endpoint(self, endpoint):
        """
        Calls a Fixer enpoint and returns the data.

        Complexity: O(1)
        """

        self.logger.info('Calling API endpoint: {0}'.format(endpoint))

        response = urllib.request.urlopen(endpoint)
        data = json.loads(response.read())

        return data


    def get_rates(self, date):
        """
        Calls the fixer historical rates endpoint and saves latest rates
        for currencies specified in the settings.py file to the DB.

        Complexity: O(n)

        :param date: Datetime object.
        """

        self.logger.info('Checking current rate')

        date = date.replace(hour=0, minute=0, second=0, microsecond=0)

        endpoint = '{0}{1}?access_key={2}&base={3}&symbols={4}'.format(
            self.api,
            date.strftime('%Y-%m-%d'),
            self.api_key,
            self.base_currency,
            ','.join(self.currencies)
        )

        data = self.call_endpoint(endpoint)

        for currency in self.currencies:
            self.create_or_update_rate(date, currency, data['rates'][currency])


    def check_rate_history(self, start_date):
        """
        Will check if at least 30 days previous rates history exists
        for the currencies provided, from the start date provided.
        If the info doesn't exist it will add the missing rate/s info to the DB.

        NOTE: Due to limitations in the current 'freemium' API subscription,
        this method calls each date independently. If the subscription were
        upgraded it would be more efficient to use the '/timeseries' API
        endpoint.

        Complexity: O(n^2) - Nested 'self.get_rates' loop.

        :param start_date: Datetime object.
        """

        self.logger.info('Checking historical rates')

        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Get previous 30 days
        dates = [start_date - timedelta(days=x) for x in range(1, 31)]

        # Remove weekends
        dates = [date for date in dates if date.weekday() < 5]

        # Call API
        for date in dates:
            # Call each date
            self.get_rates(date)


    def create_or_update_rate(self, date, currency, rate):
        """
        Will create a new entry for specified dates currencies or update the
        entry if it already exists. Update exists to preserve idempotency.

        Complexity: O(1)

        :param date: Datetime object.
        :param currency: Currency symbol.
        :param rate: Currency exchange rate.
        """

        entry = self.session.query(Rate)\
            .filter(Rate.date == date)\
            .filter(Rate.currency == currency).first()

        if entry is None:
            try:
                entry = Rate(date=date, currency=currency, rate=rate)
                self.session.add(entry)
                self.session.commit()

                self.logger.info('Checking current rate for {0}, {1}'.format(
                    date, currency
                ))

            except Exception as e:
                session.rollback()

                self.logger.error('Could not insert rates record into database.'
                                  ' Traceback: {0}'.format(str(e)))


if __name__ == '__main__':
    fixer = Fixer(API_HOME, API_KEY, BASE_CURRENCY, CURRENCIES, session)
    fixer.check_rate_history(datetime.now())
    fixer.get_rates(datetime.now())