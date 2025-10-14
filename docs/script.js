console.log("🎯 JS загружен!");

document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM готов!");
    
    const tg = window.Telegram?.WebApp;
    console.log("📱 Telegram WebApp:", tg);
    
    if (tg) {
        tg.expand();
        console.log("✅ WebApp инициализирован");

        console.log("📋 Доступные методы:", Object.keys(tg).filter(key => typeof tg[key] === 'function'));
    }


    document.querySelectorAll('.btn').forEach(button => { 
        button.addEventListener('click', function() {
            const product = this.dataset.product;
            const price = this.dataset.price;
            
            console.log("🛒 Нажата кнопка:", product, price);
            console.log("📱 Telegram WebApp объект:", tg);

            if (tg) {
                console.log("✅ Пробуем отправить данные...");
                
                const data = {
                    product: product,
                    price: parseInt(price)
                };
                
                console.log("📦 Данные для отправки:", data);
                

                if (tg.sendData) {
                    console.log("🚀 Используем sendData");
                    tg.sendData(JSON.stringify(data));
                }

                else if (tg.MainButton) {
                    console.log("🚀 Используем MainButton");
                    tg.MainButton.setText("Заказ отправлен!");
                    tg.MainButton.show();
                    setTimeout(() => tg.close(), 1000);
                }

                else {
                    console.log("🚀 Закрываем WebApp");
                    tg.close();
                }
                
                console.log("✅ Действие выполнено!");
                
            } else {
                console.log("❌ WebApp не доступен");
                alert(`Заказ: ${product} за ${price}₴`);
            }
        });  
    });  
});