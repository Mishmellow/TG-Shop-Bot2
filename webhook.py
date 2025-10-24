import os
from aiogram import Bot, Dispatcher

async def setup_webhook(bot: Bot, dp: Dispatcher):

    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

    if not WEBHOOK_SECRET or not WEBHOOK_URL:
        print("⚠️  Webhook переменные не найдены, используем polling")
        return False

    webhook_path = f"/webhook/{WEBHOOK_SECRET}"
    webhook_url = f"{WEBHOOK_URL}{webhook_path}"

    await bot.set_webhook(
        url=webhook_url,
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True
    )
    print(f"✅ Webhook установлен: {webhook_url}")
    return True