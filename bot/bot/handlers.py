from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from aiogram.utils.formatting import Bold, Text

from bot.api_client import create_product
from bot.config import ADMIN_TELEGRAM_IDS, API_URL, WEBAPP_URL

router = Router()

CATALOG_BUTTON_TEXT = "Открыть каталог"


def catalog_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=CATALOG_BUTTON_TEXT,
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )


def catalog_invite_text(*, with_greeting: bool) -> Text:
    parts: list = []
    if with_greeting:
        parts.append("Привет!\n\n")
    parts.append(Bold("У меня есть товары"))
    parts.append("\nНажмите кнопку ниже — откроется каталог.")
    return Text(*parts)


async def send_catalog_invite(message: Message, *, with_greeting: bool = False) -> None:
    content = catalog_invite_text(with_greeting=with_greeting)
    await message.answer(
        **content.as_kwargs(),
        reply_markup=catalog_keyboard(),
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    await send_catalog_invite(message, with_greeting=True)


@router.message(F.photo, F.caption)
async def admin_product_message(message: Message):
    await handle_admin_product(message)


@router.message(F.text)
async def text_message(message: Message):
    await send_catalog_invite(message)


async def handle_admin_product(message: Message):
    if not message.from_user or message.from_user.id not in ADMIN_TELEGRAM_IDS:
        await message.answer("Нет прав для создания товара.")
        return

    name = (message.caption or "").strip()
    if not name:
        await message.answer("Укажите название товара в подписи к фото.")
        return

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    if not file.file_path:
        await message.answer("Не удалось загрузить фото.")
        return

    from io import BytesIO

    buffer = BytesIO()
    await message.bot.download_file(file.file_path, buffer)
    data = buffer.getvalue()

    try:
        product = await create_product(
            API_URL,
            name,
            data,
            filename="product.jpg",
            content_type="image/jpeg",
        )
    except Exception as exc:
        await message.answer(f"Ошибка при сохранении товара: {exc}")
        return

    await message.answer(f"Товар «{product.get('name', name)}» создан (id={product.get('id')}).")
