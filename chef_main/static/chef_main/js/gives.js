document.addEventListener('DOMContentLoaded', function() {
    // Получаем CSRF токен для Django

    const remains = JSON.parse(document.getElementById('remains_id').textContent);

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
    if (isNaN(amountNum)) {
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

    return fetch('api/update-issued-count/', {
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
            date: String(date),
            day_key: getActiveDayKey()
        })
    });
}

    // Получение текущей даты в формате YYYY-MM-DD
    function getCurrentDate() {
        const datebar = document.querySelector('[data-role="datebar"]');
        const selected = datebar && datebar.dataset && datebar.dataset.date;
        if (selected) {
            return selected;
        }
        const now = new Date();
        return now.toISOString().split('T')[0];
    }

    function getActiveDayKey() {
        const activeButton = document.querySelector('.chef_serving_day.is-active');
        return activeButton ? activeButton.dataset.day : null;
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
            const current2 = parseInt(availableElement.textContent) || 0;
            availableElement.textContent = newAvailable !== undefined ? newAvailable : current2;
            console.log(newAvailable);
            // Анимация обновления
            availableElement.classList.add('updated');
            setTimeout(() => {
                availableElement.classList.remove('updated');
            }, 300);
        }

        const finalIssued = newIssued !== undefined ? newIssued : (parseInt(issuedElement?.textContent) || 0);
        updateReturnButtonState(row, finalIssued);
    }

    function updateReturnButtonState(row, issuedCount) {
        const returnBtn = row.querySelector('.return-btn');
        if (!returnBtn) {
            return;
        }

        if (issuedCount <= 0) {
            returnBtn.disabled = true;
            returnBtn.classList.add('disabled');
        } else {
            returnBtn.disabled = false;
            returnBtn.classList.remove('disabled');
        }
    }

    document.querySelectorAll('.day_menu_row').forEach(row => {
        const issuedValue = parseInt(row.querySelector('.issued-count')?.textContent) || 0;
        updateReturnButtonState(row, issuedValue);
    });

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
            const currentIssued = parseInt(row.querySelector('.issued-count')?.textContent) || 0;

            if (action === 'return' && currentIssued <= 0) {
                showNotification('Нечего возвращать', 'info');
                return;
            }

            // Блокируем кнопку на время запроса
            button.disabled = true;
            button.classList.add('loading');

            try {
                // Отправляем запрос на сервер

                const response = await updateMealCount(mealId, action, amount);
                console.log(response);
                if (!response.ok) {
                    throw new Error('Ошибка сервера');
                }

                const result = await response.json();

                if (result.success) {
                    // Обновляем отображение с новыми данными из сервера
                    console.log(result.available_count);
                    updateDisplay(row, result.issued_count, result.available_count);

                    // Показываем уведомление об успехе
                    showNotification(`${action === 'issue' ? 'Выдано' : 'Возвращено'} ${amount} порций: ${mealName}`, 'success');
                } else {
                    throw new Error(result.error || 'Ошибка при обновлении');
                }

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

    // Стили для анимаций
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

        .return-btn.disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .issued-count.updated,
        .available-count.updated,
        .ordered-count.updated {
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
            console.log(response);
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
                updateDisplay(row, meal.issued, meal.available, meal.ordered);
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


    class DatePicker {
    constructor(container) {
        this.container = container;
        this.currentDate = new Date(this.container.dataset.date);
        this.selectedDate = new Date(this.container.dataset.date);
        this.weekStart = new Date(this.container.dataset.weekStart);
        this.weekEnd = new Date(this.container.dataset.weekEnd);

        this.init();
        this.setupEventListeners();
    }

    init() {
        this.updateDisplay();
    }

    // Получение текущей выбранной даты
    getSelectedDate() {
        return new Date(this.selectedDate);
    }

    // Получение даты в формате YYYY-MM-DD
    getSelectedDateString() {
        return this.selectedDate.toISOString().split('T')[0];
    }

    // Получение даты в формате DD.MM.YYYY
    getSelectedDateFormatted() {
        return this.formatDate(this.selectedDate);
    }

    // Обновление отображения
    updateDisplay() {
        // Обновляем главную дату
        const dateDisplay = this.container.querySelector('[data-role="date-display"]');
        if (dateDisplay) {
            dateDisplay.textContent = this.formatDate(this.selectedDate);
        }

        // Обновляем активный день
        const dayButtons = this.container.querySelectorAll('[data-role="weekday-switch"] button');
        const selectedDateStr = this.selectedDate.toISOString().split('T')[0];

        dayButtons.forEach(button => {
            if (button.dataset.date === selectedDateStr) {
                button.classList.add('is-active');
            } else {
                button.classList.remove('is-active');
            }
        });

        // Обновляем диапазон недели
        const weekLabel = this.container.querySelector('[data-role="week-label"]');
        if (weekLabel) {
            weekLabel.textContent = `${this.formatDate(this.weekStart)} - ${this.formatDate(this.weekEnd)}`;
        }

        // Обновляем data-атрибуты
        this.container.dataset.date = selectedDateStr;
        this.container.dataset.weekStart = this.weekStart.toISOString().split('T')[0];
        this.container.dataset.weekEnd = this.weekEnd.toISOString().split('T')[0];

        // Вызываем событие изменения даты
        this.triggerDateChange();
    }

    // Форматирование даты в DD.MM.YYYY
    formatDate(date) {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    }

    // Переключение на определенный день
    selectDay(dateString) {
        const newDate = new Date(dateString);
        if (!isNaN(newDate.getTime())) {
            this.selectedDate = newDate;
            this.updateDisplay();
        }
    }

    // Переключение на предыдущую неделю
    prevWeek() {
        this.weekStart.setDate(this.weekStart.getDate() - 7);
        this.weekEnd.setDate(this.weekEnd.getDate() - 7);
        this.selectedDate.setDate(this.selectedDate.getDate() - 7);
        this.updateWeekButtons();
        this.updateDisplay();
    }

    // Переключение на следующую неделю
    nextWeek() {
        this.weekStart.setDate(this.weekStart.getDate() + 7);
        this.weekEnd.setDate(this.weekEnd.getDate() + 7);
        this.selectedDate.setDate(this.selectedDate.getDate() + 7);
        this.updateWeekButtons();
        this.updateDisplay();
    }

    // Обновление кнопок дней недели
    updateWeekButtons() {
        const dayButtons = this.container.querySelectorAll('[data-role="weekday-switch"] button');
        const startDate = new Date(this.weekStart);

        dayButtons.forEach((button, index) => {
            const currentDate = new Date(startDate);
            currentDate.setDate(startDate.getDate() + index);

            const dateString = currentDate.toISOString().split('T')[0];
            button.dataset.date = dateString;

            // Обновляем текст кнопки (Пн, Вт, и т.д.)
            const daysOfWeek = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
            const dayIndex = currentDate.getDay();
            const dayName = index < 5 ? button.textContent : daysOfWeek[dayIndex];
            button.textContent = dayName;
        });
    }

    // Событие изменения даты
    triggerDateChange() {
        const event = new CustomEvent('dateChange', {
            detail: {
                date: this.getSelectedDate(),
                dateString: this.getSelectedDateString(),
                formattedDate: this.getSelectedDateFormatted(),
                weekStart: this.weekStart.toISOString().split('T')[0],
                weekEnd: this.weekEnd.toISOString().split('T')[0]
            },
            bubbles: true
        });
        this.container.dispatchEvent(event);
    }

    // Настройка обработчиков событий
    setupEventListeners() {
        // Обработчики для кнопок дней
        const dayButtons = this.container.querySelectorAll('[data-role="weekday-switch"] button');
        dayButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.selectDay(button.dataset.date);
            });
        });

        // Обработчики для переключения недель
        const prevWeekBtn = this.container.querySelector('[data-action="week-prev"]');
        const nextWeekBtn = this.container.querySelector('[data-action="week-next"]');

        if (prevWeekBtn) {
            prevWeekBtn.addEventListener('click', () => this.prevWeek());
        }

        if (nextWeekBtn) {
            nextWeekBtn.addEventListener('click', () => this.nextWeek());
        }
    }

    // Публичные методы для управления извне
    setDate(date) {
        const newDate = new Date(date);
        if (!isNaN(newDate.getTime())) {
            this.selectedDate = newDate;
            this.updateDisplay();
        }
    }

    setWeek(startDate, endDate) {
        const newStart = new Date(startDate);
        const newEnd = new Date(endDate);

        if (!isNaN(newStart.getTime()) && !isNaN(newEnd.getTime())) {
            this.weekStart = newStart;
            this.weekEnd = newEnd;
            this.selectedDate = newStart;
            this.updateDisplay();
        }
    }
}

const datebar = document.querySelector('[data-role="datebar"]');
    if (datebar) {
        const datePicker = new DatePicker(datebar);

        // Пример использования из JavaScript:
        // Получение текущей даты
        console.log('Текущая дата:', datePicker.getSelectedDate());
        console.log('Текущая дата (строка):', datePicker.getSelectedDateString());
        console.log('Текущая дата (форматированная):', datePicker.getSelectedDateFormatted());

        // Установка новой даты
        // datePicker.setDate('2026-01-20');

        // Установка новой недели
        // datePicker.setWeek('2026-01-26', '2026-01-30');

        // Подписка на события изменения даты
        datebar.addEventListener('dateChange', (event) => {
            console.log('Дата изменена:', event.detail);
            // Здесь можно обновить данные на странице
            // Например: loadDataForDate(event.detail.dateString);
        });

        // Сохранение экземпляра для глобального доступа
        window.datePicker = datePicker;
    }

});
