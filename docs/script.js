const tg = window.Telegram.WebApp;

document.addEventListener('DOMContentLoaded', function() {
    tg.expand();
    tg.BackButton.show();
    
    tg.BackButton.onClick(function(){
        tg.close();
    });

    document.querySelectorAll('.btn').forEach(button => { 
        button.addEventListener('click', function() {
            const product = this.dataset.product;
            const price = this.dataset.price;

            tg.sendData(JSON.stringify({
                action: 'order_delivery',
                product: product,
                price: price
            }));
            tg.close();
        });  
    });  
});  