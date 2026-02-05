document.addEventListener('DOMContentLoaded', function() {
    // Получаем CSRF токен для Django
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

    const csrftoken = getCookie('csrftoken');

    // Функция для отправки AJAX запроса
    // Убедитесь что все переменные определены
function updateMealCount(mealId, action, amount) {
    // Проверяем входные данные
    if (!mealId) {
        console.error('mealId не определен:', mealId);
        throw new Error('ID блюда не указан');
    }

    if (!action || !['issue', 'return'].includes(action)) {
        console.error('Некорректное действие:', action);
        throw new Error('Некорректное действие');
    }

    const amountNum = parseInt(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
        console.error('Некорректное количество:', amount);
        throw new Error('Некорректное количество');
    }

    // Получаем дату
    const date = getCurrentDate();
    if (!date) {
        console.error('Дата не определена');
        throw new Error('Ошибка получения даты');
    }

    console.log('Отправка данных:', {
        meal_id: mealId,
        action: action,
        amount: amountNum,
        date: date
    });

    return fetch('/api/update-issued-count/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            meal_id: String(mealId),  // Преобразуем в строку на всякий случай
            action: String(action),
            amount: amountNum,
            date: String(date)
        })
    });
}

    // Получение текущей даты в формате YYYY-MM-DD
    function getCurrentDate() {
        const now = new Date();
        return now.toISOString().split('T')[0];
    }

    // Обновление отображения счетчиков
    function updateDisplay(row, newIssued, newAvailable) {
        const issuedElement = row.querySelector('.issued-count');
        const availableElement = row.querySelector('.available-count');

        if (issuedElement) {
            const current = parseInt(issuedElement.textContent) || 0;
            issuedElement.textContent = newIssued !== undefined ? newIssued : current;

            // Анимация обновления
            issuedElement.classList.add('updated');
            setTimeout(() => {
                issuedElement.classList.remove('updated');
            }, 300);
        }

        if (availableElement) {
            const current = parseInt(availableElement.textContent) || 0;
            availableElement.textContent = newAvailable !== undefined ? newAvailable : current;

            // Анимация обновления
            availableElement.classList.add('updated');
            setTimeout(() => {
                availableElement.classList.remove('updated');
            }, 300);
        }
    }

    // Обработчик кликов по кнопкам
    document.addEventListener('click', async function(event) {
        const issueBtn = event.target.closest('.issue-btn');
        const returnBtn = event.target.closest('.return-btn');

        if (issueBtn || returnBtn) {
            event.preventDefault();

            const button = issueBtn || returnBtn;
            const mealId = button.getAttribute('data-meal-id');
            const action = button.getAttribute('data-action'); // 'issue' или 'return'
            const amount = parseInt(button.getAttribute('data-amount'));
            const row = button.closest('.day_menu_row');
            const mealName = row.getAttribute('data-meal-name');

            // Блокируем кнопку на время запроса
            button.disabled = true;
            button.classList.add('loading');

            try {
                // Отправляем запрос на сервер
                const result = await updateMealCount(mealId, action, amount);

                // Обновляем отображение
                updateDisplay(row, result.issued_count, result.available_count);

                // Показываем уведомление об успехе
                showNotification(`${action === 'issue' ? 'Выдано' : 'Возвращено'} ${amount} порций: ${mealName}`, 'success');

            } catch (error) {
                // Показываем ошибку
                showNotification(`Ошибка: ${error.message}`, 'error');
                console.error('Ошибка при обновлении:', error);
            } finally {
                // Разблокируем кнопку
                button.disabled = false;
                button.classList.remove('loading');
            }
        }
    });

    // Функция для показа уведомлений
    function showNotification(message, type = 'info') {
        // Создаем элемент уведомления
        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.textContent = message;

        // Стили для уведомления
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            backgroundColor: type === 'success' ? '#4CAF50' :
                           type === 'error' ? '#F44336' : '#2196F3',
            zIndex: '9999',
            fontFamily: "'M PLUS Rounded 1c', sans-serif",
            fontWeight: '500',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            animation: 'slideIn 0.3s ease'
        });

        // Добавляем в DOM
        document.body.appendChild(notification);

        // Удаляем через 3 секунды
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Стили для анимаций (можно добавить в CSS)
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }

        .day_menu_btn.loading {
            opacity: 0.7;
            cursor: wait;
            position: relative;
        }

        .day_menu_btn.loading::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 16px;
            height: 16px;
            margin: -8px 0 0 -8px;
            border: 2px solid #fff;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .issued-count.updated,
        .available-count.updated {
            animation: pulse 0.3s ease;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .notification {
            font-family: 'M PLUS Rounded 1c', sans-serif;
        }
    `;
    document.head.appendChild(style);

    // Функция для загрузки всех данных по приёму пищи
    async function loadMealData(mealType) {
        try {
            const response = await fetch(`/api/get-meal-data/?meal_type=${mealType}&date=${getCurrentDate()}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const data = await response.json();
                updateAllCounts(mealType, data);
            }
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
        }
    }

    // Обновление всех счетчиков в таблице
    function updateAllCounts(mealType, data) {
        const tableBody = document.querySelector(`[data-meal="${mealType}"]`);
        if (!tableBody) return;

        data.meals.forEach(meal => {
            const row = tableBody.querySelector(`[data-meal-id="${meal.id}"]`);
            if (row) {
                updateDisplay(row, meal.issued_count, meal.available_count);
            }
        });
    }

    // Автообновление каждые 30 секунд
    setInterval(() => {
        const activeTab = document.querySelector('.day_menu_tab_input:checked');
        if (activeTab) {
            const mealType = activeTab.id;
            loadMealData(mealType);
        }
    }, 30000);

    // Обработчик переключения вкладок
    document.querySelectorAll('.day_menu_tab_input').forEach(tab => {
        tab.addEventListener('change', function() {
            if (this.checked) {
                loadMealData(this.id);
            }
        });
    });
});
