from pymongo import MongoClient

class MongoConnection:

    __instance = None

    def __init__(self, url_conn: str) -> None:
        self.url_conn = url_conn
        if MongoConnection.__instance is None:
            MongoConnection.__instance = MongoClient(url_conn)
        else:
            raise Exception('You cannot create another Mongo connection')

    @staticmethod
    def get_instance(url_conn: str) -> object:
        if not MongoConnection.__instance:
            MongoConnection(url_conn)
        return MongoConnection.__instance

    @staticmethod
    def close_instance() -> None:
        MongoConnection.__instance.close()