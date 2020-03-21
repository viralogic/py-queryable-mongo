from datetime import datetime
from . import LeagueModel, SaleModel, StudentModel


class MongoData(object):
    def __init__(self, db):
        self.db = db

    def seed_data(self):
        self._add_sales()
        self._add_students()
        self._add_teams()

    def _add_students(self):
        data = [{"quizzes": [10, 62], "labs": [51]}]
        self.db[StudentModel.__collection_name__].insert_many(data)

    def _add_sales(self):
        data = [
            {
                "item": "abc",
                "price": 10,
                "quantity": 2,
                "date": datetime(
                    year=2014, month=1, day=1, hour=8, minute=0, second=0
                ),
            },
            {
                "item": "jkl",
                "price": 20,
                "quantity": 1,
                "date": datetime(
                    year=2014, month=2, day=3, hour=9, minute=0, second=0
                ),
            },
            {
                "item": "xyz",
                "price": 5,
                "quantity": 5,
                "date": datetime(
                    year=2014, month=2, day=3, hour=9, minute=5, second=0
                ),
            },
            {
                "item": "abc",
                "price": 10,
                "quantity": 10,
                "date": datetime(
                    year=2014, month=2, day=15, hour=8, minute=0, second=0
                ),
            },
            {
                "item": "xyz",
                "price": 5,
                "quantity": 10,
                "date": datetime(
                    year=2014, month=2, day=15, hour=9, minute=5, second=0
                ),
            },
        ]
        self.db[SaleModel.__collection_name__].insert_many(data)

    def _add_teams(self):
        data = [
            {
                "name": "Western Hockey League",
                "short_name": "WHL",
                "seasons": [
                    {
                        "start_year": 2018,
                        "end_year": 2019,
                        "teams": [
                            {
                                "name": "Kamloops Blazers",
                                "city": "Kamloops",
                                "region": "BC",
                                "country": "CAN",
                                "arenas": [
                                    {
                                        "name": "Sandman Centre",
                                        "capacity": 5419,
                                        "website": None,
                                        "contact": {
                                            "email": "info@blazerhockey.com",
                                            "phone": "250-828-1144",
                                        },
                                    }
                                ],
                            },
                            {
                                "name": "Kelowna Rockets",
                                "city": "Kelowna",
                                "region": "BC",
                                "country": "CAN",
                                "arenas": [
                                    {
                                        "name": "Prospera Place",
                                        "capacity": 6007,
                                        "website": None,
                                        "contact": {
                                            "email": "info@kelownarockets.com",
                                            "phone": "250-860-7825",
                                        },
                                    }
                                ],
                            },
                        ],
                    }
                ],
            }
        ]
        self.db[LeagueModel.__collection_name__].insert_many(data)
