from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import os
import requests
from dotenv import load_dotenv
import logging
from io import BytesIO

logging.basicConfig(level=logging.INFO)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
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


    print("DEBUG: API_URL =", API_URL)
    # Отправка в backend
    try:
        
        response = requests.post(f"{API_URL}/generate", json={"image_url": file_url})
        logging.info("DEBUG: response_data =", response.text)
        if response.ok:
            data = response.json()

            if "error" in data:
                await message.answer(f"❌ Ошибка генерации: {data['error']}")
                return

            image = data.get("result_url")
            if not image or not image.endswith((".jpg", ".jpeg", ".png")):
                await message.answer("Ошибка: backend вернул некорректную ссылку на изображение.")
                return

            img_resp = requests.get(image)
            if img_resp.ok:
                await message.answer_photo(BytesIO(img_resp.content), caption="Готово! 😈")
            else:
                await message.answer("❌ Не удалось загрузить изображение с backend.")
        else:
            await message.answer("❌ Backend вернул ошибку.")
    except Exception as e:
        await message.answer(f"❌ Ошибка связи с backend: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
