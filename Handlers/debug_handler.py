from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message()
async def debug_all_messages(message: Message):
    print(f"🔍 DEBUG UPDATE: {message}")
    print(f"🔍 Content type: {message.content_type}")
    print(f"🔍 WebApp data: {message.web_app_data}")
    print(f"🔍 Full message: {message.model_dump_json(indent=2)}")