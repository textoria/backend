import json
from typing import Dict, Any
from decouple import config
from fastapi import HTTPException

from db import Text, db, ActionHistory

import orjson as json
from fastapi import FastAPI
from aiokeydb import KeyDBClient


keydb_uri = config("KEYDB_URI")

KeyDBClient.init_session(
    uri=keydb_uri,
)

app = FastAPI()


async def store_keys_to_database(data: Dict[str, Any]):
    for key, value in data.items():
        text_obj, _ = await db.get_or_create(Text, key=key, defaults={"text": value})
        if text_obj.text != value:
            text_obj.text = value
            await db.update(text_obj)


async def load_keys() -> Dict[str, Any]:
    keys = await db.execute(Text.select().where(Text.deleted == False))
    if not keys:
        with open("keys.json", "r") as f:
            data = json.loads(f.read())
        await store_keys_to_database(data)
    else:
        data = {key.key: key.text for key in keys}
    return data


async def update_key(key: str, new_value: Any) -> Dict[str, Any]:
    text_obj = await db.get(Text, key=key)
    if not text_obj:
        raise KeyError(f"Key '{key}' not found.")

    text_before = text_obj.text
    text_obj.text = new_value
    await db.update(text_obj)

    await db.create(ActionHistory, text=text_obj, action="update",
                    data=json.dumps({"old_value": text_before, "new_value": new_value}))

    # Update KeyDB
    await KeyDBClient.async_hmset("cache", {key: new_value})

    return {key: new_value}


@app.put("/update_key")
async def update_key_route(key: str, new_value: str):
    try:
        updated_key = await update_key(key, new_value)
        return updated_key
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


async def load_json_data(filename: str) -> str:
    with open(filename, "r") as f:
        data = f.read()
    return data


async def store_keys_to_keydb(data: Dict[str, Any]):
    await KeyDBClient.async_hmset("cache", data)


async def get_all_keys() -> Dict[str, Any]:
    keys = await KeyDBClient.async_hgetall("cache")
    return keys


@app.on_event("startup")
async def on_startup():
    data = await load_keys()
    await KeyDBClient.async_flushdb()  # Resets all keys in KeyDB
    await store_keys_to_keydb(data)


@app.get("/get_all_keys")
async def get_all_keys_route():
    return await get_all_keys()


async def create_key(new_key: str, new_value: Any) -> Dict[str, Any]:
    text_obj, created = await db.get_or_create(Text, key=new_key, defaults={"text": new_value})
    if not created:
        raise ValueError(f"Key '{new_key}' already exists.")

    # Add the new key to KeyDB
    await KeyDBClient.async_hmset("cache", {new_key: new_value})

    # Store the creation action
    await db.create(ActionHistory, action="create", text=text_obj,
                    data=json.dumps({"key": new_key, "value": new_value}))

    return {new_key: new_value}


@app.post("/create_key")
async def create_key_route(new_key: str, new_value: str):
    try:
        created_key = await create_key(new_key, new_value)
        return created_key
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def delete_key(key: str) -> Dict[str, str]:
    text_obj = await db.get(Text, key=key)
    if not text_obj:
        raise KeyError(f"Key '{key}' not found.")

    text_obj.deleted = True
    await db.update(text_obj)

    # Remove the key from KeyDB
    await KeyDBClient.async_hdel("cache", key)

    # Store the deletion action
    await db.create(ActionHistory, action="delete", text=text_obj)

    return {"detail": f"Key '{key}' deleted."}


@app.delete("/delete_key")
async def delete_key_route(key: str):
    try:
        deleted_key = await delete_key(key)
        return deleted_key
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
