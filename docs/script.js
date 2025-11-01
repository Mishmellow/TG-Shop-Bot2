// const tg = window.Telegram.WebApp;
// let cart = [];
//
// function updateMainButton() {
//     const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
//     const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
//
//     if (totalItems > 0) {
//         tg.MainButton.setText(`Оформить Заказ (${totalPrice} грн)`);
//         tg.MainButton.show();
//     } else {
//         tg.MainButton.hide();
//     }
// }
//
// function addToCart(productData) {
//     const existingItem = cart.find(item => item.product === productData.product);
//
//     if (existingItem) {
//         existingItem.quantity += 1;
//     } else {
//         cart.push({
//             product: productData.product,
//             name: productData.name,
//             price: productData.price,
//             quantity: 1
//         });
//     }
//
//     updateMainButton();
//     tg.HapticFeedback.notificationOccurred('success');
// }
//
// tg.ready();
// tg.expand();
// updateMainButton();
//
// document.querySelectorAll('.add-to-cart-btn').forEach(button => {
//     button.addEventListener('click', () => {
//         const product = button.getAttribute('data-product');
//         const price = parseInt(button.getAttribute('data-price'));
//         const name = button.getAttribute('data-name');
//
//         addToCart({ product, price, name });
//     });
// });
//
// tg.MainButton.onClick(() => {
//     const dataToSend = JSON.stringify({ items: cart });
//     tg.sendData(dataToSend);
// });