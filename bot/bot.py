from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import asyncio
import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Отправь фото девушки, и я покажу магию 🤖")

@dp.message()
async def image_handler(message: Message):
    if not message.photo:
        await message.answer("Пожалуйста, отправь фото")
        return
    file = await bot.get_file(message.photo[-1].file_id)
    file_path = file.file_path
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    # Отправка в backend
    response = requests.post(f"{API_URL}/generate", json={"image_url": file_url})
    if response.ok:
        image = response.json()["result_url"]
        await message.answer_photo(image, caption="Готово! 😈")
    else:
        await message.answer("Что-то пошло не так...")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
