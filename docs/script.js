console.log("🎯 JS загружен!");

// ПРОВЕРЯЕМ существует ли Telegram WebApp
const tg = window.Telegram?.WebApp;

document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM готов!");
    
    if (tg) {
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
                tg.sendData(JSON.stringify({
                    action: 'order_delivery',
                    product: product,
                    price: price
                }));
                tg.close();
            } else {
                alert(`Заказ: ${product} за ${price}₴\n(В Telegram отправится автоматически)`);
            }
        });  
    });  
});