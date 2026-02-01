document.addEventListener('DOMContentLoaded', () => {
    const adminMenuDateDiv = document.querySelector('.admin_menu_date');
    const dayButtons = document.querySelectorAll('.admin_menu_day');

    // Функция для обновления даты
    function updateAdminMenuDate(dayOfWeekText) {
        // Здесь вы можете реализовать логику для получения реальной даты
        // Например, если у вас есть текущая дата, вы можете сдвинуть её
        // В этом примере просто подставим текст дня недели

        // Получаем текущую дату (для примера, можно брать из глобальной переменной)
        const currentDate = new Date(); // Сегодняшняя дата
        let dayToDisplay = '';

        switch (dayOfWeekText) {
            case 'Пн':
                // Находим ближайший понедельник
                currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 1); // 1 = понедельник
                dayToDisplay = 'Понедельник';
                break;
            case 'Вт':
                // Находим ближайший вторник
                currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 2); // 2 = вторник
                dayToDisplay = 'Вторник';
                break;
            case 'Ср':
                // Находим ближайшую среду
                currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 3); // 3 = среда
                dayToDisplay = 'Среда';
                break;
            case 'Чт':
                // Находим ближайший четверг
                currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 4); // 4 = четверг
                dayToDisplay = 'Четверг';
                break;
            case 'Пт':
                // Находим ближайшую пятницу
                currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 5); // 5 = пятница
                dayToDisplay = 'Пятница';
                break;
            default:
                dayToDisplay = 'Неизвестный день';
                break;
        }

        // Форматируем дату (DD.MM.YYYY)
        const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
        const formattedDate = currentDate.toLocaleDateString('ru-RU', options);

        adminMenuDateDiv.textContent = `${dayToDisplay}, ${formattedDate}`;
    }

    // Добавляем обработчик события click для каждой кнопки дня недели
    dayButtons.forEach(button => {
        button.addEventListener('click', () => {
            const dayText = button.textContent; // Получаем текст кнопки ("Пн", "Вт" и т.д.)
            updateAdminMenuDate(dayText);

            // Опционально: можно добавить класс активности для нажатой кнопки
            dayButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });

    // Инициализация: установить текущий день недели при загрузке страницы
    // (или тот, который вы хотите показывать по умолчанию)
    const today = new Date();
    const todayDayOfWeek = today.toLocaleDateString('ru-RU', { weekday: 'long' });
    const todayFormattedDate = today.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
    adminMenuDateDiv.textContent = `${todayDayOfWeek}, ${todayFormattedDate}`;

    // Также можно сделать активной кнопку для текущего дня недели
    const currentDayAbbr = today.toLocaleDateString('ru-RU', { weekday: 'short' });
    dayButtons.forEach(button => {
        if (button.textContent === currentDayAbbr) {
            button.classList.add('active');
        }
    });
});
