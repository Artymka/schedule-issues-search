import asyncpg
import asyncio
from contextlib import contextmanager

from asyncmixin import AsyncMixin


@contextmanager
def db_cursor():
    conn = dbpool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
            conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        dbpool.putconn(conn)

class DB(AsyncMixin):
    async def __ainit__(self, min_size, max_size, **connect_kwargs):
        self.pool = await asyncpg.pool.create_pool(min_size=min_size, max_size=max_size, **connect_kwargs)
        await self.create_tables()

    async def create_tables(self):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute("""
                    CREATE TABLE IF NOT EXISTS targets (
                        id INTEGER PRIMARY KEY,
                        title VARCHAR(120),
                        ical_link VARCHAR(100)
                    )
                """)
                await con.execute("""
                    CREATE TABLE IF NOT EXISTS issues_types (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(120)
                    )
                """)
                await con.execute("""
                    CREATE TABLE IF NOT EXISTS issues (
                        id SERIAL PRIMARY KEY,
                        target_id INTEGER,
                        first_lesson_dt TIMESTAMP,
                        second_lesson_dt TIMESTAMP,
                        first_lesson_title VARCHAR(100),
                        second_lesson_title VARCHAR(100),
                        type_id INTEGER
                    )                
                """)

    async def get_all_targets(self):
        async with self.pool.acquire() as con:
            res = await con.fetch("""
                SELECT * FROM targets
            """)

            return res

    async def update_targets(self, targets: list[dict]):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute("""
                    TRUNCATE targets
                """)

                for target in targets:
                    await con.execute("""
                        INSERT INTO targets
                        (id, title, ical_link)
                        VALUES ($1, $2, $3)
                    """,
                    target["id"], target["title"], target["ical_link"])

    async def get_all_issues_with_descs(self):
        async with self.pool.acquire() as con:
            res = await con.fetch("""
                SELECT target_id,
                       first_lesson_dt,
                       second_lesson_dt,
                       first_lesson_title,
                       second_lesson_title,
                       type_id,
                       issues_types.title AS desc
                FROM issues
                LEFT JOIN issues_types
                ON issues.type_id = issues_types_id
            """)

            return res

    async def get_filtered_issues_with_desc(self, filter: str):
        async with self.pool.acquire() as con:
            res = await con.fetch("""
                SELECT first_lesson_dt,
                       second_lesson_dt,
                       first_lesson_title,
                       second_lesson_title,
                       type_id,
                       issues_types.title AS desc
                FROM issues
                LEFT JOIN issues_types
                ON issues.type_id = issues_types_id
                LEFT JOIN targets
                ON issues.target_id = targets.id
            """)

            return res

    async def update_issues(self):
        pass

    async def update_issues_types(self):
        pass

async def main():
    db = await DB(min_size=1, max_size=10,
                  host="127.0.0.1",
                  database="postgres",
                  port=5432,
                  user="postgres",
                  password="root")

if __name__ == "__main__":
    asyncio.run(main())


