import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# ССЫЛКА НА ТВОЮ СТАТЬЮ
ARTICLE_LINK = "https://telegra.ph/Kak-vyjti-na-dohod-ot-500-000-rublej-v-mesyac-iz-doma-razbor-mehaniki-sovremennyh-cifrovyh-professij-07-07"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID") 
CHANNEL_LINK = os.getenv("CHANNEL_LINK") 
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        print(f"Статус пользователя {user_id} в канале: {member.status}")
        if member.status in ["creator", "administrator", "member"]:
            return True
        return False
    except Exception as e:
        # Теперь мы строго блокируем доступ при ошибке и выводим её в логи Render
        print(f"КРИТИЧЕСКАЯ ОШИБКА ПРОВЕРКИ: {e}")
        return False

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    subscribed = await is_user_subscribed(user_id)
    
    if subscribed:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 Читать статью", url=ARTICLE_LINK)]
        ])
        await message.answer("🎉 Спасибо за подписку! Ваша статья доступна по кнопке ниже:", reply_markup=kb)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👉 Подписаться на канал", url=CHANNEL_LINK)],
            [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]
        ])
        await message.answer("Чтобы получить доступ к статье, пожалуйста, подпишитесь на наш канал!", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "check_sub")
async def process_check_sub(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    subscribed = await is_user_subscribed(user_id)
    
    if subscribed:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 Читать статью", url=ARTICLE_LINK)]
        ])
        await callback_query.message.answer("Отлично! Вот ваша ссылка на статью:", reply_markup=kb)
        await callback_query.answer()
    else:
        await callback_query.answer("Вы всё еще не подписались на канал или подписка не обновилась 😢", show_alert=True)

async def on_startup(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
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
