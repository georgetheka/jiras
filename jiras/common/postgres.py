from dataclasses import dataclass
from typing import Optional, List, Dict, Any

import psycopg2

from jiras.common.settings import Settings


class PostgresException(BaseException):
    pass


@dataclass
class QueryResult:
    result_set: List[Any]
    columns: List[str]


class Postgres:
    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    def exec(self,
             query: str,
             read_params: Optional[Dict] = None,
             write_params: Optional[List[Dict]] = None,
             ) -> Optional[QueryResult]:
        conn = None
        query_result: Optional[QueryResult] = None
        try:
            conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.username,
                password=self.password,
            )
            cur = conn.cursor()
            if write_params:
                for p in write_params:
                    cur.execute(query, p)
                cur.close()
                conn.commit()
            else:
                cur.execute(query, read_params)
                query_result = QueryResult(
                    result_set=cur.fetchall(),
                    columns=[desc[0] for desc in cur.description],
                )
                cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            raise PostgresException(error)
        finally:
            if conn is not None:
                conn.close()

        return query_result


def make_postgres(settings: Settings) -> Postgres:
    return Postgres(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_database,
        username=settings.db_user,
        password=settings.db_pass
    )
