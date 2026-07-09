import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Подтягиваем настройки из Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID") 
CHANNEL_LINK = os.getenv("CHANNEL_LINK") 
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL") # Render сам подставит этот адрес

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            return True
        return False
    except Exception:
        return False

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if await is_user_subscribed(user_id):
        await message.answer("Спасибо за подписку! Вот ваш файл:")
        # Твоя ссылка на файл (замени на свою)
        await message.answer_document(document="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👉 Подписаться на канал", url=CHANNEL_LINK)],
            [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]
        ])
        await message.answer("Чтобы получить бесплатный файл, пожалуйста, подпишитесь на наш канал!", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "check_sub")
async def process_check_sub(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await is_user_subscribed(user_id):
        await callback_query.message.answer("Отлично! Держи свой файл:")
        await callback_query.message.answer_document(document="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")
        await callback_query.answer()
    else:
        await callback_query.answer("Вы всё еще не подписались на канал 😢", show_alert=True)

async def on_startup(bot: Bot):
    # Устанавливаем вебхук в Telegram
    await bot.set_webhook(f"{RENDER_EXTERNAL_URL}/webhook")

def main():
    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

if __name__ == "__main__":
    main()
