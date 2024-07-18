from aiogram import Dispatcher, Bot, F, filters, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from googletrans import Translator
import asyncio
import nltk
from nltk.corpus import wordnet

nltk.download("wordnet")
nltk.download("omw-1.4")

translator = Translator()

bot = Bot(token="7205282559:AAFnCHpyabuxAYI5IZ78JwDUyW_Z8Nqf39Q")
dp = Dispatcher(bot=bot)

dest_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="ru"), KeyboardButton(text="en"), KeyboardButton(text="uz")]
],resize_keyboard=True)
src_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="ru"), KeyboardButton(text="en"), KeyboardButton(text="uz")]
], resize_keyboard=True)

class Lang(StatesGroup):
    dest = State()
    src = State()
    text = State()

@dp.message(filters.CommandStart())
async def start_bot(message: Message, state: FSMContext):
    await state.set_state(Lang.dest)
    await message.answer("Qaysi tilga tarjima qilmoqchisiz?\ntilni o'zgartirish uchun /change_language ni yozing", reply_markup=dest_kb)

@dp.message(Lang.dest)
async def dest_bot(message: Message, state: FSMContext):
    await state.update_data(dest=message.text)
    await state.set_state(Lang.src)
    await message.answer("qaysi tilda matn yozmoqchisiz?", reply_markup=src_kb)

@dp.message(Lang.src)
async def src_bot(message: Message, state: FSMContext):
    await state.update_data(src=message.text)
    await state.set_state(Lang.text)
    await message.answer("Endi matn yozing")

@dp.message(Lang.text)
async def test_bot(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    text = translator.translate(text=message.text, dest=data["dest"], src=data["src"]).text
    await message.answer(text=f"{text}")
    await state.clear()

@dp.message(filters.Command("change_language"))
async def change_lang(message: Message, state: FSMContext):
    await state.set_state(Lang.dest)
    await message.answer("Qaysi tilga tarjima qilmoqchisiz?", reply_markup=dest_kb)

@dp.message(Lang.src)
async def changed_src_bot(message: Message, state: FSMContext):
    await state.update_data(src=message.text)
    await state.set_state(Lang.text)
    await message.answer("Endi matn yozing")

@dp.message(Lang.text)
async def changed_test_bot(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    text = translator.translate(text=message.text, dest=data["dest"], src=data["src"]).text
    await message.answer(text=f"{text}")
    await state.clear()

@dp.message(F.text)
async def translate(message: Message):
    lang = translator.detect(message.text)
    if lang == "en":
        text = translator.translate(message.text, dest="uz", src="en").text
        synonym = wordnet.synonyms(text, lang="uz")
        syn = ""
        for i in synonym:
            syn += f" {i}"
        await message.answer(text=f"so'z - {text}\nsinonimlari - {syn}")
    text = translator.translate(message.text, dest="en").text
    synonym = wordnet.synonyms(text)
    syn = ""
    for i in synonym:
        for j in i:
            syn += f" {j},"

    await message.answer(text=f"translated word - {text}\nsynonyms - {syn}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
