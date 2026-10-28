from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import close_pool, get_pool
from app.schemas import ProductOut
from app.storage import check_minio, upload_image

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    yield
    await close_pool()


app = FastAPI(title="Catalog API", lifespan=lifespan)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    pool = await get_pool()
    db_ok = False
    try:
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False
    minio_ok = check_minio()
    status = "ok" if db_ok and minio_ok else "degraded"
    return {"status": status, "database": db_ok, "minio": minio_ok}


@app.get("/api/products", response_model=list[ProductOut])
async def list_products():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, image_url, created_at
            FROM products
            ORDER BY created_at DESC
            """
        )
    return [
        ProductOut(
            id=r["id"],
            name=r["name"],
            image_url=r["image_url"],
            created_at=r["created_at"],
        )
        for r in rows
    ]


@app.post("/api/products", response_model=ProductOut, status_code=201)
async def create_product(
    name: str = Form(...),
    image: UploadFile = File(...),
):
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Product name is required")

    content_type = image.content_type or ""
    extension = ALLOWED_CONTENT_TYPES.get(content_type)
    if extension is None:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty image file")
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    image_key, image_url = upload_image(data, content_type, extension)

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO products (name, image_key, image_url)
            VALUES ($1, $2, $3)
            RETURNING id, name, image_url, created_at
            """,
            name,
            image_key,
            image_url,
        )

    return ProductOut(
        id=row["id"],
        name=row["name"],
        image_url=row["image_url"],
        created_at=row["created_at"],
    )
