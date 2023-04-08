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
    db_config = {
        "database": parsed_url.path[1:],
        "user": parsed_url.username,
        "host": parsed_url.hostname,
        "port": parsed_url.port,
        "password": parsed_url.password,
    }
    return db_config


db_url = config('DATABASE_URL')
db_config = parse_db_url(db_url)

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

    language = CharField(max_length=20, default="ru", null=False)

    text = TextField(null=True)


class EditHistory(BaseModel):
    text = ForeignKeyField(Text, backref="edit_history")

    text_before = TextField(null=True)
    text_after = TextField(null=True)

    created_at = DateTimeTZField(default=now, null=False)


database.evolve(
        ignore_tables=[
            "basemodel"
        ],
        interactive=False,
    )

db = peewee_async.Manager(database)

database.set_allow_sync(False)
