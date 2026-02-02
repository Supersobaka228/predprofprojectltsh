document.addEventListener('DOMContentLoaded', () => {
    const statusCellClass = '.js-status-cell';

    document.addEventListener('click', async (e) => {
        // Проверяем, нажата ли кнопка одобрения или отклонения
        const btn = e.target.closest('.js-order-btn');
        if (!btn) return;

        const row = btn.closest('.orders_row');
        const orderId = row.dataset.orderId;
        const action = btn.dataset.action; // "allowed" или "rejected"
        const statusCell = row.querySelector(statusCellClass);

        try {
            const response = await fetch('/update-order-status/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // Функция получения токена ниже
                },
                body: JSON.stringify({
                    id: orderId,
                    status: action
                })
            });

            if (response.ok) {
                // Если в Пите успешно обновилось, меняем HTML в этой ячейке
                if (action === 'allowed') {
                    statusCell.innerHTML = '<span class="orders_status orders_status--approved">Одобрено</span>';
                } else {
                    statusCell.innerHTML = '<span class="orders_status orders_status--rejected">Отклонено</span>';
                }
                // Убираем класс с кнопками, если нужно по стилям
                statusCell.classList.remove('orders_cell--actions');
            } else {
                alert('Ошибка при обновлении статуса');
            }
        } catch (error) {
            console.error('Ошибка:', error);
        }
    });
});

// Функция для работы с CSRF-токеном в Django
function getCookie(name) {
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
