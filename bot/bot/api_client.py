import aiohttp
from aiohttp import FormData


async def create_product(api_url: str, name: str, photo_bytes: bytes, filename: str, content_type: str) -> dict:
    form = FormData()
    form.add_field("name", name)
    form.add_field(
        "image",
        photo_bytes,
        filename=filename,
        content_type=content_type or "image/jpeg",
    )
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/api/products", data=form) as resp:
            body = await resp.json(content_type=None)
            if resp.status >= 400:
                detail = body.get("detail") if isinstance(body, dict) else str(body)
                raise RuntimeError(f"API error {resp.status}: {detail}")
            return body
