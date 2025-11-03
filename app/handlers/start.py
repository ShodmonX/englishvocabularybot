from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from app.middlewares import StartMiddleware


router = Router()

router.message.middleware(StartMiddleware())

@router.message(CommandStart())
async def start(message: Message):
    text = """
👋 Salom! Men English Word Helper botiman

Bu yerda siz inglizcha so‘zlarning:
• O‘zbek tilidagi ma’nolarini 🇺🇿  
• Talaffuzini 🔊  
• Rasmini 🖼️  
• Va hatto so‘zning audio talaffuzini ham 🎧  
topishingiz mumkin!

Shunchaki istalgan inglizcha so‘zni yozing — men sizga barcha ma’nolarini chiqarib berishga harakat qilaman ✨  

Boshlaymizmi? 😊
"""
    await message.answer(text)


@router.message(Command(commands=["help"]))
async def help(message: Message):
    text = """
📖 Yordam bo‘limiga xush kelibsiz!

Quyidagi komandalar orqali botdan samarali foydalanishingiz mumkin:

🔹 So‘z yuborish — inglizcha so‘zni yuboring, men sizga uning ma’nolari, talaffuzi va rasmini chiqaraman.  
🔹 /help — shu yordam oynasini qayta ochish.  

Agar sizda taklif yoki biror xatolik bo‘lsa — admin bilan bog‘laning: @XolmurodovShodmon 🛠️
"""
    await message.answer(text)
