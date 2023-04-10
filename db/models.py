import datetime
import peewee_async

from peewee import *
from decouple import config
from playhouse.postgres_ext import DateTimeTZField
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

import peeweedbevolve


def now():
    return datetime.datetime.now(tz=ZoneInfo("UTC"))


def parse_db_url(db_url: str):
    parsed_url = urlparse(db_url)
    db_conf = {
        "database": parsed_url.path[1:],
        "user": parsed_url.username,
        "host": parsed_url.hostname,
        "port": parsed_url.port,
        "password": parsed_url.password,
    }
    return db_conf


db_config = parse_db_url(config('DATABASE_URL'))

database = peewee_async.PostgresqlDatabase(
    database=db_config['database'],
    user=db_config['user'],
    host=db_config['host'],
    port=db_config['port'],
    password=db_config['password']
)


class BaseModel(Model):
    class Meta:
        database = database


class Text(BaseModel):
    key = TextField(unique=False, index=True, null=False)

    class Meta:
        table_name = "text"


class Translation(BaseModel):
    text = ForeignKeyField(Text, backref="translations")

    language = TextField(null=False)

    translation = TextField(null=False)

    created_at = DateTimeTZField(default=now, null=False)

    class Meta:
        table_name = "translation"
        indexes = (
            (("text", "language"), True),
        )


database.evolve(
        ignore_tables=[
            "basemodel"
        ],
        interactive=False,
    )

db = peewee_async.Manager(database)

database.set_allow_sync(False)
