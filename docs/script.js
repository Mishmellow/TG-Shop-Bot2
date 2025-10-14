console.log("🎯 JS загружен!");

const tg = window.Telegram?.WebApp;

document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM готов!");
    console.log("📱 Telegram WebApp:", tg);

    if (tg) {
        console.log("🎯 Инициализируем Telegram WebApp...");
        tg.expand();
        tg.BackButton.show();

        tg.BackButton.onClick(function(){
            tg.close();
        });
    } else {
        console.log("❌ Telegram WebApp не найден (запускай в Telegram)");
    }

    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            const product = this.dataset.product;
            const price = this.dataset.price;
            console.log("🛒 Нажата кнопка:", product, price);

            if (tg) {
                console.log("✅ Отправляем данные в Telegram...");

                const orderData = {
                    product: product,
                    price: parseInt(price)
                };

                console.log("📦 Отправляемые данные:", orderData);
                tg.sendData(JSON.stringify(orderData));

            } else {
                console.log("❌ Telegram WebApp не найден!");
                alert(`Заказ: ${product} за ${price}₴\n(В Telegram отправится автоматически)`);
            }
        });
    });
});