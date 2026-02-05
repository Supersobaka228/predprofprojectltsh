document.addEventListener('DOMContentLoaded', () => {
    const statusCellClass = '.js-status-cell';
    const dateDisplay = document.querySelector('.orders_date');
    const prevButton = document.querySelector('.orders_nav_btn');
    const nextButton = document.querySelector('.orders_nav_btn--next');
    const tableBody = document.querySelector('.orders_table_body');

    const formatDateDisplay = (date) => {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = String(date.getFullYear()).slice(-2);
        return `${day}.${month}.${year}`;
    };

    const formatDateParam = (date) => {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        return `${date.getFullYear()}-${month}-${day}`;
    };

    const renderOrders = (orders) => {
        if (!tableBody) {
            return;
        }
        tableBody.innerHTML = '';
        orders.forEach((order) => {
            const row = document.createElement('div');
            row.className = 'orders_row';
            row.dataset.orderId = order.id;
            row.innerHTML = `
                <div class="orders_cell">${order.id}</div>
                <div class="orders_cell">${order.date}</div>
                <div class="orders_cell">${order.user}</div>
                <div class="orders_cell">${order.items}</div>
                <div class="orders_cell">${order.summ} ₽</div>
                <div class="orders_cell orders_cell--actions js-status-cell">
                    ${order.status === 'allowed'
                        ? '<span class="orders_status orders_status--approved">Одобрено</span>'
                        : order.status === 'rejected'
                            ? '<span class="orders_status orders_status--rejected">Отклонено</span>'
                            : '<button class="orders_action_btn orders_action_btn--accept js-order-btn" type="button" data-action="allowed"><img src="/static/icon/check.svg" alt=""></button><button class="orders_action_btn orders_action_btn--reject js-order-btn" type="button" data-action="rejected"><img src="/static/icon/close.svg" alt=""></button>'}
                </div>
            `;
            tableBody.appendChild(row);
        });
    };

    const loadOrdersByDate = async (date) => {
        if (!dateDisplay) {
            return;
        }
        dateDisplay.textContent = formatDateDisplay(date);
        try {
            const response = await fetch(`/admin_main/buyorders/?date=${formatDateParam(date)}`);
            if (!response.ok) {
                renderOrders([]);
                return;
            }
            const payload = await response.json();
            renderOrders(payload.orders || []);
        } catch (error) {
            console.error('Ошибка загрузки заявок:', error);
            renderOrders([]);
        }
    };

    let currentDate = new Date();

    if (dateDisplay && prevButton && nextButton) {
        loadOrdersByDate(currentDate);

        prevButton.addEventListener('click', () => {
            currentDate.setDate(currentDate.getDate() - 1);
            loadOrdersByDate(currentDate);
        });

        nextButton.addEventListener('click', () => {
            currentDate.setDate(currentDate.getDate() + 1);
            loadOrdersByDate(currentDate);
        });
    }

    document.addEventListener('click', async (e) => {
        const btn = e.target.closest('.js-order-btn');
        if (!btn) return;

        const row = btn.closest('.orders_row');
        const orderId = row.dataset.orderId;
        const action = btn.dataset.action;
        const statusCell = row.querySelector(statusCellClass);

        try {
            const response = await fetch('/update-order-status/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    id: orderId,
                    status: action
                })
            });

            if (response.ok) {
                if (action === 'allowed') {
                    statusCell.innerHTML = '<span class="orders_status orders_status--approved">Одобрено</span>';
                } else {
                    statusCell.innerHTML = '<span class="orders_status orders_status--rejected">Отклонено</span>';
                }
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
