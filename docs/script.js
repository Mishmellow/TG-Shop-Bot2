console.log("🎯 JS загружен!");

document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM готов!");

    const tg = window.Telegram?.WebApp;
    console.log("📱 Telegram WebApp:", tg);

    if (tg) {
        console.log("🎯 Инициализируем Telegram WebApp...");
        tg.expand();
        tg.enableClosingConfirmation();

        // Показываем кнопку "Назад"
        if (tg.BackButton) {
            tg.BackButton.show();
            tg.BackButton.onClick(function(){
                tg.close();
            });
        }
    } else {
        console.log("❌ Telegram WebApp не найден (запускай в Telegram)");
    }


    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            const product = this.dataset.product;
            const price = this.dataset.price;

            console.log("🛒 Нажата кнопка:", product, price);
            console.log("📱 Telegram WebApp:", tg);

            if (tg && tg.sendData) {
                console.log("✅ Отправляем данные в Telegram...");


                const orderData = {
                    product: product,
                    price: parseInt(price)
                };

                console.log("📦 Отправляемые данные:", orderData);

                tg.sendData(JSON.stringify(orderData));
                console.log("📤 Данные отправлены!");

            } else {
                console.log("❌ Telegram WebApp не найден!");
                alert(`Заказ: ${product} за ${price}₴\n(В Telegram отправится автоматически)`);
            }
        });
    });
});