console.log("🎯 JS загружен!");

document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM готов!");
    
    const tg = window.Telegram.WebApp;
    console.log("📱 Telegram WebApp версия:", tg.version);
    console.log("📱 Telegram WebApp platform:", tg.platform);
    
    if (tg) {
        tg.expand();
        console.log("✅ WebApp инициализирован");
    }

    document.querySelectorAll('.btn').forEach(button => { 
        button.addEventListener('click', function() {
            const product = this.dataset.product;
            const price = this.dataset.price;
            
            console.log("🛒 Нажата кнопка:", product, price);
            
            if (tg && tg.sendData) {
                console.log("✅ sendData доступен!");
                
                const data = {
                    product: product,
                    price: parseInt(price)
                };
                
                console.log("📦 Отправляем данные:", data);
                
                try {

                    tg.sendData(JSON.stringify(data));
                    console.log("✅ sendData вызван успешно!");
                    

                    setTimeout(() => {
                        console.log("🔒 Закрываем WebApp...");
                        tg.close();
                    }, 1000);
                    
                } catch (error) {
                    console.log("❌ Ошибка при sendData:", error);
                }
                
            } else {
                console.log("❌ sendData не доступен");
                alert(`Заказ: ${product} за ${price}₴`);
            }
        });  
    });  
});