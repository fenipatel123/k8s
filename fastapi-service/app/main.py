from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncpg
import os

app = FastAPI(title="FastAPI Service (PostgreSQL)")

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "apppass")

pool: asyncpg.Pool | None = None

class ItemIn(BaseModel):
    name: str
    description: Optional[str] = None

class Item(ItemIn):
    id: int

@app.on_event("startup")
async def on_startup():
    global pool
    pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
        min_size=1,
        max_size=5,
    )
    async with pool.acquire() as conn:
        await conn.execute(
            '''CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );'''
        )

@app.on_event("shutdown")
async def on_shutdown():
    if pool:
        await pool.close()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/items", response_model=List[Item])
async def list_items():
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, description FROM items ORDER BY id")
        return [Item(id=r["id"], name=r["name"], description=r["description"]) for r in rows]

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    async with pool.acquire() as conn:
        r = await conn.fetchrow("SELECT id, name, description FROM items WHERE id=$1", item_id)
        if not r:
            raise HTTPException(status_code=404, detail="Item not found")
        return Item(id=r["id"], name=r["name"], description=r["description"])

@app.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemIn):
    async with pool.acquire() as conn:
        r = await conn.fetchrow(
            "INSERT INTO items (name, description) VALUES ($1,$2) RETURNING id,name,description",
            item.name, item.description
        )
        return Item(id=r["id"], name=r["name"], description=r["description"])

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemIn):
    async with pool.acquire() as conn:
        r = await conn.fetchrow(
            "UPDATE items SET name=$1, description=$2 WHERE id=$3 RETURNING id,name,description",
            item.name, item.description, item_id
        )
        if not r:
            raise HTTPException(status_code=404, detail="Item not found")
        return Item(id=r["id"], name=r["name"], description=r["description"])

@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    async with pool.acquire() as conn:
        res = await conn.execute("DELETE FROM items WHERE id=$1", item_id)
        if res.split()[-1] == "0":
            raise HTTPException(status_code=404, detail="Item not found")
    return None
