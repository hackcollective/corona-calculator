import datetime

from data.utils import build_country_data


class Countries:
    def __init__(self, timestamp):
        self.country_data, self.last_modified, self.historical_country_data = (
            build_country_data()
        )
        self.countries = list(self.country_data.keys())
        self.default_selection = self.countries.index("Canada")
        self.timestamp = timestamp

    @property
    def stale(self):
        delta = datetime.datetime.utcnow() - self.timestamp
        return delta > datetime.timedelta(hours=1)
