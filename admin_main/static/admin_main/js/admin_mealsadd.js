document.addEventListener('DOMContentLoaded', function() {
    const dishesContainer = document.getElementById('dishes-container');
    const addDishBtn = document.querySelector('.add-dish-btn');
    let dishCounter = 1;

    const getMenuOptionsHtml = (selector) => {
        const firstMenu = document.querySelector(selector);
        return firstMenu ? firstMenu.innerHTML : '';
    };

    const updateDishFieldNames = (block, index) => {
        block.setAttribute('data-dish-index', index);

        block.querySelectorAll('input[name^="allergens_"]').forEach((input) => {
            input.name = `allergens_${index}[]`;
        });

        block.querySelectorAll('input[name^="ingredients_"]').forEach((input) => {
            if (input.type === 'hidden') {
                input.name = `ingredients_${index}[]`;
            }
        });

        block.querySelectorAll('input[name^="ingredients_grams_"]').forEach((input) => {
            input.name = `ingredients_grams_${index}[]`;
        });
    };

    // Делегирование событий для аллергенов (работает и для динамических элементов)
    function setupEventDelegation() {
        // Клик по кнопке "Добавить" аллерген (делегирование)
        dishesContainer.addEventListener('click', function(e) {

            // Клик по варианту аллергена в меню


            // Клик по кнопке удаления аллергена


            // Клик по кнопке удаления блюда
            if (e.target && e.target.classList.contains('remove-dish-btn')) {
                e.preventDefault();
                e.stopPropagation();

                const removeBtn = e.target;
                const dishBlock = removeBtn.closest('.dish-block');
                if (dishBlock) {
                    removeDishBlock(dishBlock);
                }
            }
        });

        // Закрытие меню аллергенов при клике вне его


        // Закрытие меню при нажатии Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.menu_config_allergen_menu').forEach(menu => {
                    menu.style.display = 'none';
                });
            }
        });
    }

    // Функция для добавления нового блюда
    function addNewDish() {
        dishCounter++;

        const newDishBlock = document.createElement('div');
        newDishBlock.className = 'menu_config_block dish-block';
        newDishBlock.setAttribute('data-dish-index', dishCounter - 1);

        const allergensMenuHtml = getMenuOptionsHtml('.menu_config_allergen_menu');
        const ingredientsMenuHtml = getMenuOptionsHtml('.menu_config_ingredient_menu');

        newDishBlock.innerHTML = `
            <div class="menu_config_dish">
                <div class="menu_config_dish_top">
                    <span class="menu_config_dish_label">Блюдо <span class="dish-number">${dishCounter}</span></span>
                    <button type="button" class="remove-dish-btn">×</button>
                </div>

                <div class="menu_config_dish_row">
                    <input class="menu_config_input menu_config_input--name" type="text" name="dish_name[]" placeholder="Название блюда" required>
                    <input class="menu_config_input menu_config_input--small" type="number" name="dish_weight[]" placeholder="Вес (г)" min="0">
                    <input class="menu_config_input menu_config_input--small" type="number" name="dish_kcal[]" placeholder="Ккал" min="0">
                </div>

                <div class="menu_config_dish_row">
                    <span class="menu_config_dish_label">Аллергены</span>
                    <div class="menu_config_allergens" aria-live="polite"></div>
                    <div class="menu_config_allergen_picker">
                        <button class="menu_config_add" type="button">Добавить</button>
                        <div class="menu_config_allergen_menu" role="listbox" aria-label="Аллергены">
                            ${allergensMenuHtml}
                        </div>
                    </div>
                </div>

                <div class="menu_config_dish_row">
                    <span class="menu_config_dish_label">Состав</span>
                    <div class="menu_config_ingredients" aria-live="polite"></div>
                    <div class="menu_config_ingredient_picker">
                        <button class="menu_config_add" type="button" aria-haspopup="listbox" aria-expanded="false">Добавить</button>
                        <div class="menu_config_ingredient_menu" role="listbox" aria-label="Ингредиенты">
                            ${ingredientsMenuHtml}
                        </div>
                    </div>
                </div>
            </div>

            <div class="menu_config_requests">
                <div class="menu_config_requests_title">Заявки, связанные с блюдом</div>
                <div class="menu_config_requests_list">
                    <span class="menu_config_requests_item">Молоко пастеризованное</span>
                    <span class="menu_config_requests_item">Крупа гречневая</span>
                </div>
            </div>
        `;

        dishesContainer.appendChild(newDishBlock);
        updateDishNumbers();

        // Прокручиваем к новому блоку
        newDishBlock.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        console.log(`Добавлено блюдо #${dishCounter}`);
    }

    // Функция для удаления блока блюда
    function removeDishBlock(block) {
        const allBlocks = document.querySelectorAll('.dish-block');
        if (allBlocks.length > 1) {
            block.remove();
            updateDishNumbers();
            dishCounter = allBlocks.length - 1;
        } else {
            alert('Должно остаться хотя бы одно блюдо!');
        }
    }

    // Функция для обновления нумерации блюд
    function updateDishNumbers() {
        const dishBlocks = document.querySelectorAll('.dish-block');
        dishBlocks.forEach((block, index) => {
            const numberSpan = block.querySelector('.dish-number');
            if (numberSpan) {
                numberSpan.textContent = index + 1;
            }
            block.setAttribute('data-dish-index', index);
            updateDishFieldNames(block, index);

            // Показываем/скрываем кнопку удаления
            const removeBtn = block.querySelector('.remove-dish-btn');
            if (removeBtn) {
                removeBtn.style.display = dishBlocks.length > 1 ? 'block' : 'none';
            }
        });
    }

    // Инициализация
    function init() {
        // Настройка делегирования событий
        setupEventDelegation();

        // Обработчик для кнопки добавления блюда
        if (addDishBtn) {
            addDishBtn.addEventListener('click', addNewDish);
        }

        // Инициализация нумерации
        updateDishNumbers();

        // Обработчик отправки формы
        const form = document.querySelector('.menu_configurator_form');
        if (form) {
            form.addEventListener('submit', function(e) {
                const dishNames = this.querySelectorAll('input[name="dish_name[]"]');
                let hasEmpty = false;

                dishNames.forEach(input => {
                    if (!input.value.trim()) {
                        hasEmpty = true;
                        input.style.borderColor = 'red';
                    } else {
                        input.style.borderColor = '';
                    }
                });

                if (hasEmpty) {
                    e.preventDefault();
                    alert('Пожалуйста, заполните названия всех блюд!');
                }
            });
        }
    }

    // Запуск инициализации
    init();
});