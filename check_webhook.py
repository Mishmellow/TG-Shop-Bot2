import requests
import json
import os

TOKEN = "7979006531:AAE6KatiHFo_fc5ItEVMzrzclETbI6rtHik"

API_URL = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"


def check_webhook_status():
    print("--- Проверка статуса Webhook через Telegram API ---")

    if not TOKEN:
        print("🛑 Ошибка: Пожалуйста, вставьте ваш актуальный токен бота в переменную TOKEN.")
        return

    try:
        response = requests.get(API_URL)
        response.raise_for_status()

        data = response.json()

        if data['ok']:
            info = data['result']
            print("\n✅ Успешный ответ от Telegram:")
            print(json.dumps(info, indent=4, ensure_ascii=False))

            current_railway_url = "https://worker-production-8177.up.railway.app/webhook/dev_secret_123"

            print(f"\nТекущий URL вебхука (в Telegram): {info.get('url', 'НЕ УСТАНОВЛЕН')}")
            print(f"Ожидаемый URL (на Railway): {current_railway_url}")
            print(f"Количество необработанных обновлений: {info.get('pending_update_count', 0)}")

            if info.get('url') and info['url'] != current_railway_url:
                print("\n🚨 ВНИМАНИЕ: URL, установленный в Telegram, НЕ СОВПАДАЕТ с вашим Railway URL. Это проблема.")

            if info.get('pending_update_count', 0) > 0:
                print(
                    f"🚨 ВНИМАНИЕ: Есть {info['pending_update_count']} необработанных обновлений, которые блокируют новые.")
                print(
                    "Решение: В run.py раскомментируйте 'await bot.delete_webhook(drop_pending_updates=True)' в on_startup, чтобы удалить их при следующем запуске.")

            if info.get('last_error_message'):
                print(f"❌ ПОСЛЕДНЯЯ ОШИБКА TELEGRAM: {info['last_error_message']}")

        else:
            print(f"\n❌ Ошибка API Telegram: {data.get('description', 'Нет описания')}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Ошибка при выполнении HTTP-запроса: {e}")
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    check_webhook_status()