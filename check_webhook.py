import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    print("🛑 Ошибка: Токен не найден в .env файле.")
    print("Добавьте в .env: BOT_TOKEN=ваш_токен")
    exit(1)

API_URL = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"


def check_webhook_status():
    print("--- Проверка статуса Webhook через Telegram API ---")

    try:
        response = requests.get(API_URL)
        response.raise_for_status()

        data = response.json()

        if data['ok']:
            info = data['result']
            print("\n✅ Успешный ответ от Telegram:")
            print(json.dumps(info, indent=4, ensure_ascii=False))

            webhook_url = info.get('url', '')
            pending = info.get('pending_update_count', 0)

            print(f"\nТекущий URL вебхука: {webhook_url if webhook_url else '❌ НЕ УСТАНОВЛЕН (Polling режим)'}")
            print(f"Количество необработанных обновлений: {pending}")

            if webhook_url:
                print("\n⚠️ Webhook активен! Для Polling режима нужно его удалить:")
                print(f"curl \"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true\"")
            else:
                print("\n✅ Webhook отключен. Можно использовать Polling режим.")

            if pending > 0:
                print(f"\n⚠️ ВНИМАНИЕ: Есть {pending} необработанных обновлений.")
                print("Они будут обработаны при следующем запуске бота.")

            if info.get('last_error_message'):
                print(f"\n❌ ПОСЛЕДНЯЯ ОШИБКА: {info['last_error_message']}")
                print(f"Время ошибки: {info.get('last_error_date', 'Неизвестно')}")

        else:
            print(f"\n❌ Ошибка API Telegram: {data.get('description', 'Нет описания')}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Ошибка HTTP запроса: {e}")
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")


def delete_webhook():
    print("\n--- Удаление Webhook ---")
    delete_url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true"

    try:
        response = requests.get(delete_url)
        data = response.json()

        if data['ok']:
            print("✅ Webhook успешно удалён!")
        else:
            print(f"❌ Ошибка: {data.get('description', 'Неизвестно')}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    print("1. Проверить статус webhook")
    print("2. Удалить webhook")
    choice = input("\nВыберите действие (1 или 2): ").strip()

    if choice == "1":
        check_webhook_status()
    elif choice == "2":
        delete_webhook()
    else:
        print("❌ Неверный выбор")