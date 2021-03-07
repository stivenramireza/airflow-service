import pyodbc

class SQLServerConnection:

    __instance = None

    def __init__(self, url_conn: str) -> None:
        self.url_conn = url_conn
        if SQLServerConnection.__instance is None:
            SQLServerConnection.__instance = pyodbc.connect(url_conn)
        else:
            raise Exception('You cannot create another SQL Server connection')

    @staticmethod
    def get_instance(url_conn: str) -> object:
        if not SQLServerConnection.__instance:
            SQLServerConnection(url_conn)
        return SQLServerConnection.__instance

    @staticmethod
    def close_instance() -> None:
        SQLServerConnection.__instance.close()