import asyncpg
import asyncio
from contextlib import contextmanager

from asyncmixin import AsyncMixin


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
                        short_title VARCHAR(120),
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
                        (id, title, short_title, ical_link)
                        VALUES ($1, $2, $3, $4)
                    """,
                    target["id"], target["title"], target["short_title"], target["ical_link"])

    async def get_all_issues(self):
        async with self.pool.acquire() as con:
            res = await con.fetch("""
                SELECT targets.title AS target_title,
                       first_lesson_dt,
                       second_lesson_dt,
                       first_lesson_title,
                       second_lesson_title,
                       type_id,
                       issues_types.title AS desc
                FROM issues
                LEFT JOIN issues_types
                ON issues.type_id = issues_types_id
                LEFT JOIN targets
                ON target_id == targets.id
            """)

            return res

    async def get_filtered_issues(self, search_filter: str):
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
                WHERE targets.title LIKE "%$1%"
            """,
            search_filter)

            return res

    async def update_issues(self, issues: list[dict]):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute("""
                    TRUNCATE issues
                """)

                for i in issues:
                    await con.execute("""
                        INSERT INTO issues
                        (id, target_id, first_lesson_dt, second_lesson_dt, 
                        first_lesson_title, second_lesson_title, type_id)
                        VALUES ($1, $2, $3, $4)
                    """,
                    i["id"], i["target_id"], i["first_lesson_dt"], i["second_lesson_dt"],
                    i["first_lesson_title"], i["second_lesson_title"], i["type_id"])

    async def update_issues_types(self, issues_types):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute("""
                    TRUNCATE issues_types
                """)

                for it in issues_types:
                    await con.execute("""
                        INSERT INTO issues_types
                        (id, title)
                        VALUES ($1, $2)
                    """,
                    it["id"], it["title"])

async def main():
    db = await DB(min_size=1, max_size=10,
                  host="127.0.0.1",
                  database="schedule_issues",
                  port=5432,
                  user="postgres",
                  password="root")

    await db.update_issues_types([
        {"id": 1, "title": "филоса"},
        {"id": 2, "title": "кросис"},
    ])

if __name__ == "__main__":
    asyncio.run(main())


