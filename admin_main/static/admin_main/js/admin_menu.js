document.addEventListener('DOMContentLoaded', () => {
    const adminMenuDateDiv = document.querySelector('.admin_menu_date');
    const dayButtons = document.querySelectorAll('.admin_menu_day');
    const dayInput = document.getElementById('day_input_value');

    const dayMap = {
        'Пн': 1,
        'Вт': 2,
        'Ср': 3,
        'Чт': 4,
        'Пт': 5,
    };

    function updateAdminMenuDate(dayOfWeekText) {

        const currentDate = new Date(); // Сегодняшняя дата
        let dayToDisplay = '';
        if (dayInput) {
            dayInput.value = dayMap[dayOfWeekText] || '';
        }

        const dayValue = dayInput ? dayInput.value : (dayMap[dayOfWeekText] || '');
        if (dayValue) {
            document.dispatchEvent(new CustomEvent('menuDayChange', {
                detail: { day: dayValue }
            }));
        }

        switch (dayOfWeekText) {
            case 'Пн':
                currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 1); // 1 = понедельник
                dayToDisplay = 'Понедельник';
                break;
            case 'Вт':
                currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 2); // 2 = вторник
                dayToDisplay = 'Вторник';
                break;
            case 'Ср':
                currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 3); // 3 = среда
                dayToDisplay = 'Среда';
                break;
            case 'Чт':
                currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 4); // 4 = четверг
                dayToDisplay = 'Четверг';
                break;
            case 'Пт':
                currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 5); // 5 = пятница
                dayToDisplay = 'Пятница';
                break;
            default:
                dayToDisplay = 'Неизвестный день';
                break;
        }

        const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
        const formattedDate = currentDate.toLocaleDateString('ru-RU', options);

        adminMenuDateDiv.textContent = `${dayToDisplay}, ${formattedDate}`;
    }

    dayButtons.forEach(button => {
        button.addEventListener('click', () => {
            const dayText = button.textContent;
            updateAdminMenuDate(dayText);

            dayButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });

    const today = new Date();
    const todayDayOfWeek = today.toLocaleDateString('ru-RU', { weekday: 'long' });
    const todayFormattedDate = today.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
    adminMenuDateDiv.textContent = `${todayDayOfWeek}, ${todayFormattedDate}`;

    const currentDayAbbr = today.toLocaleDateString('ru-RU', { weekday: 'short' });
    dayButtons.forEach(button => {
        if (button.textContent === currentDayAbbr) {
            button.classList.add('active');
            updateAdminMenuDate(button.textContent);
        }
    });

    if (dayInput && !dayInput.value) {
        const first = dayButtons[0];
        if (first) {
            updateAdminMenuDate(first.textContent);
        }
    }
});
