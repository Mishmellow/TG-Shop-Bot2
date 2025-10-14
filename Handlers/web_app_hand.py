# from aiogram import Router
# from aiogram.types import Message
# import json
#
# router = Router()
#
#
# @router.message()
# async def catch_webapp_data(message: Message):
#     # Ловим ВСЁ что приходит
#     print(f"🔍 Получено сообщение: {message.text}")
#     print(f"🔍 WebApp data: {message.web_app_data}")
#     print(f"🔍 ВСЁ сообщение: {message}")
#     print("---")
#
#     # Если есть данные из веб-приложения
#     if message.web_app_data:
#         print("🎯🎯🎯 WEBAPP ДАННЫЕ НАКОНЕЦ-ТО!")
#         data = json.loads(message.web_app_data.data)
#         await message.answer(f"🎉 УРА! Получил: {data}")
#         return
#
#
#     return