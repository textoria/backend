import peewee
from .models import db


async def exists(query: peewee.Select | peewee.ModelCompoundSelectQuery) -> bool:
    if not isinstance(query, (peewee.Select, peewee.ModelCompoundSelectQuery)):
        raise ValueError('EXISTS support only SELECT query')
    result = await db.execute(query)
    return len(result) != 0
