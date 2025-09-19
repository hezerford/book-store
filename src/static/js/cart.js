/**
 * AJAX функциональность для управления корзиной
 * Обновление количества товаров без перезагрузки страницы
 */

class CartManager {
    constructor(cartItemSelector, quantitySelector, subtotalSelector, totalSelector) {
        this.cartItemSelector = cartItemSelector || '.quantity-btn';
        this.quantitySelector = quantitySelector || '.quantity-display';
        this.subtotalSelector = subtotalSelector || '.cart-item-subtotal';
        this.totalSelector = totalSelector || '#cart-total';
        this.init();
    }

    init() {
        this.bindEventHandlers();
    }

    bindEventHandlers() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.attachButtonHandlers();
            });
        } else {
            this.attachButtonHandlers();
        }
    }

    attachButtonHandlers() {
        const buttons = document.querySelectorAll(this.cartItemSelector);

        buttons.forEach(button => {
            button.removeEventListener('click', this.handleClick);
            button.addEventListener('click', this.handleClick.bind(this));
        });
    }

    handleClick(e) {
        e.preventDefault();
        e.stopPropagation();

        const button = e.currentTarget;
        const action = button.dataset.action;
        const bookId = button.dataset.bookId;

        if (action && bookId) {
            this.updateCartQuantity(bookId, action);
        }
    }

    /**
     * Обновляет количество товара в корзине через AJAX
     * @param {string} bookId - Slug книги
     * @param {string} action - Действие: 'plus' или 'minus'
     * @param {number|null} newQuantity - Новое количество (опционально)
     */
    async updateCartQuantity(bookId, action, newQuantity = null) {
        const formData = new FormData();

        if (newQuantity !== null) {
            formData.append('quantity', newQuantity);
        } else {
            formData.append('action', action);
        }

        const quantityElement = document.getElementById('quantity-' + bookId);
        const originalQuantity = quantityElement?.textContent?.trim();

        // Показываем индикатор загрузки
        this.showLoading(quantityElement);

        // Получаем CSRF токен
        const csrfToken = this.getCsrfToken();

        try {
            const response = await fetch(`/cart/update-item/${bookId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });

            const data = await response.json();

            if (data.success) {
                if (data.removed) {
                    // Если товар удалён, обновляем страницу
                    this.showNotification(data.message, 'success');
                    setTimeout(() => location.reload(), 1500);
                    return;
                }

                // Успешное обновление
                this.updateUI(bookId, data);
                this.showNotification(`Количество обновлено! Всего товаров: ${data.cart_items_count}`, 'success');

            } else {
                // Ошибка
                this.showNotification(data.error, 'error');
                this.restoreQuantity(quantityElement, originalQuantity);
            }

        } catch (error) {
            console.error('Ошибка обновления корзины:', error);
            this.showNotification('Произошла ошибка при обновлении корзины', 'error');
            this.restoreQuantity(quantityElement, originalQuantity);
        }
    }

    /**
     * Обновляет интерфейс после успешного изменения количества
     */
    updateUI(bookId, data) {
        // Обновляем отображение количества
        const quantityElement = document.getElementById('quantity-' + bookId);
        const subtotalElement = document.getElementById('subtotal-' + bookId);
        const totalElement = document.getElementById('cart-total');

        if (quantityElement) {
            quantityElement.textContent = data.quantity;
        }

        if (subtotalElement) {
            subtotalElement.textContent = `Подытог: $ ${data.item_subtotal.toFixed(2)}`;
        }

        if (totalElement) {
            totalElement.textContent = `Total price: $${data.cart_total.toFixed(2)}`;
        }
    }

    /**
     * Показывает индикатор загрузки
     */
    showLoading(element) {
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }

    /**
     * Восстанавливает количество при ошибке
     */
    restoreQuantity(element, quantity) {
        element.textContent = quantity;
    }

    /**
     * Показывает уведомление пользователю
     */
    showNotification(message, type = 'success') {
        const container = document.getElementById('notification-container') ||
            this.createNotificationContainer();

        const notification = document.createElement('div');
        notification.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0 show`;
        notification.style.cssText = `
            min-width: 300px;
            margin-bottom: 10px;
            animation: slideInRight 0.3s ease-out;
        `;

        notification.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check' : 'exclamation'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto"
                        onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        container.appendChild(notification);

        // Автоматически удаляем через 3 секунды
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Создаёт контейнер для уведомлений если его нет
     */
    createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);

        // Добавляем стили для анимаций
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        return container;
    }

    /**
     * Получает CSRF токен из формы или meta-тега
     */
    getCsrfToken() {
        // Сначала ищем в скрытых полях формы
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            return csrfToken.value;
        }

        // Если не нашли, ищем в meta-теге (обычно используется в AJAX запросах)
        csrfToken = document.querySelector('meta[name=csrf-token]');
        if (csrfToken) {
            return csrfToken.content;
        }

        console.warn('CSRF токен не найден. Добавьте {% csrf_token %} в ваш шаблон или <meta name="csrf-token" content="{{ csrf_token }}">');
        return '';
    }

    /**
     * Добавляет CSRF токен в DOM если его нет (для AJAX)
     */
    ensureCsrfToken() {
        if (!document.querySelector('[name=csrfmiddlewaretoken]') &&
            !document.querySelector('meta[name=csrf-token]')) {

            const csrfToken = document.createElement('input');
            csrfToken.type = 'hidden';
            csrfToken.name = 'csrfmiddlewaretoken';
            // Получаем из cookie или другого источника
            const token = this.getCookie('csrftoken') || document.querySelector('[name=csrf_token]')?.value;

            if (token) {
                csrfToken.value = token;
                document.body.appendChild(csrfToken);
            }
        }
    }

    /**
     * Вспомогательная функция для получения cookie
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Добавляет обработчик для изменения количества через клавиатуру
     */
    addKeyboardSupport() {
        document.addEventListener('keydown', (e) => {
            if (e.target.classList.contains('quantity-input')) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const bookId = e.target.dataset.bookId;
                    const newQuantity = parseInt(e.target.value);
                    if (!isNaN(newQuantity) && newQuantity > 0) {
                        this.updateCartQuantity(bookId, null, newQuantity);
                    }
                }
            }
        });
    }

    /**
     * Обновляет количество с учётом склада
     */
    updateWithStockCheck(bookId, newQuantity, maxStock) {
        if (newQuantity > maxStock) {
            this.showNotification(`Доступно только ${maxStock} шт.`, 'error');
            return;
        }
        this.updateCartQuantity(bookId, null, newQuantity);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    // Создаём менеджер корзины
    window.cartManager = new CartManager();

    // Добавляем CSRF токен если необходимо
    window.cartManager.ensureCsrfToken();

    // Добавляем поддержку клавиатуры
    window.cartManager.addKeyboardSupport();
});
