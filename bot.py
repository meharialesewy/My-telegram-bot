import asyncio
import uuid
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = 8807690018:AAHrgtQgqwZ71_rLckDADYzqwtfbPqfyryA
CHAPA_SECRET_KEY = CHAPA_TEST_PRIV_9bofdBrfK-Lmxufys0zNwpFNuPfF5TgoVdxi3vUw
CHAPA_BASE_URL = "https://api.chapa.co/v1/transaction"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def create_payment(amount: float, email: str, name: str, tx_ref: str):
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": name,
        "tx_ref": tx_ref
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{CHAPA_BASE_URL}/initialize", json=payload, headers=headers) as resp:
            return await resp.json()

async def verify_payment(tx_ref: str):
    headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{CHAPA_BASE_URL}/verify/{tx_ref}", headers=headers) as resp:
            return await resp.json()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(welecome! to order a product click /buy ")

@dp.message(Command("buy"))
async def buy(message: types.Message):
    tx_ref = f"tx-{message.from_user.id}-{uuid.uuid4().hex[:6]}"
    amount = 50.0
    user_name = message.from_user.first_name or "Customer"

    res = await create_payment(amount, "customer@example.com", user_name, tx_ref)

    if res.get("status") == "success":
        link = res["data"]["checkout_url"]
        btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 በቴሌብር ወይም በባንክ ይክፈሉ", url=link)],
            [InlineKeyboardButton(text="✅ ክፍያ ፈጽሜያለሁ (አረጋግጥ)", callback_data=f"check:{tx_ref}")]
        ])
        await message.answer(f"📦 የእቃ ዋጋ፦ {amount} ብር\nከታች ባለው ሊንክ ይክፈሉ፦", reply_markup=btn)
    else:
        await message.answer("የክፍያ ሊንክ ማመንጨት አልተቻለም። ቁልፎቹ ትክክል መሆናቸውን ያረጋግጡ።")

@dp.callback_query(F.data.startswith("check:"))
async def check(call: types.CallbackQuery):
    ref = call.data.split(":")[1]
    res = await verify_payment(ref)
    if res.get("status") == "success" and res.get("data", {}).get("status") == "success":
        await call.message.edit_text("🎉 ክፍያዎ ተረጋግጧል! እናመሰግናለን።")
    else:
        await call.message.answer("⚠️ ክፍያው እስካሁን አልደረሰም፤ እባክዎ ከከፈሉ በኋላ እንደገና ይሞክሩ።")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
