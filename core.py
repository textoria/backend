import json
import asyncio
from typing import Dict, Any
from decouple import config
from fastapi import HTTPException

import orjson as json
from fastapi import FastAPI
from aiokeydb import KeyDBClient


keydb_uri = config("KEYDB_URI")
print(keydb_uri)

KeyDBClient.init_session(
    uri=keydb_uri,
)

app = FastAPI()


async def update_key(key: str, new_value: Any) -> Dict[str, Any]:
    keys = json.loads(await KeyDBClient.async_get('cache'))
    if key not in keys:
        raise KeyError(f"Key '{key}' not found.")
    keys[key] = new_value
    await KeyDBClient.async_set('cache', json.dumps(keys))
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


async def store_keys_to_keydb(data: str):
    await KeyDBClient.async_set('cache', data)


async def get_all_keys() -> str:
    keys = json.loads(await KeyDBClient.async_get('cache'))
    return keys


@app.on_event("startup")
async def on_startup():
    data = await load_json_data("keys.json")
    print(keydb_uri)
    await store_keys_to_keydb(data)


@app.get("/get_all_keys")
async def get_all_keys_route():
    return await get_all_keys()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
