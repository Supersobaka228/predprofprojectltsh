document.addEventListener('DOMContentLoaded', function() {
    const initMenuConfigForm = (form) => {
        const dishesContainer = form.querySelector('[data-dishes-container]');
        const addDishBtn = form.querySelector('.add-dish-btn');
        if (!dishesContainer) {
            return;
        }

        let dishCounter = dishesContainer.querySelectorAll('.dish-block').length || 1;

        const getMenuOptionsHtml = (selector) => {
            const firstMenu = form.querySelector(selector);
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

        const setupEventDelegation = () => {
            dishesContainer.addEventListener('click', function(e) {
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

            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    document.querySelectorAll('.menu_config_allergen_menu').forEach(menu => {
                        menu.style.display = 'none';
                    });
                }
            });
        };

        const addNewDish = () => {
            dishCounter += 1;

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

            newDishBlock.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        };

        const removeDishBlock = (block) => {
            const allBlocks = dishesContainer.querySelectorAll('.dish-block');
            if (allBlocks.length > 1) {
                block.remove();
                updateDishNumbers();
                dishCounter = allBlocks.length - 1;
            } else {
                alert('Должно остаться хотя бы одно блюдо!');
            }
        };

        const updateDishNumbers = () => {
            const dishBlocks = dishesContainer.querySelectorAll('.dish-block');
            dishBlocks.forEach((block, index) => {
                const numberSpan = block.querySelector('.dish-number');
                if (numberSpan) {
                    numberSpan.textContent = index + 1;
                }
                block.setAttribute('data-dish-index', index);
                updateDishFieldNames(block, index);

                const removeBtn = block.querySelector('.remove-dish-btn');
                if (removeBtn) {
                    removeBtn.style.display = dishBlocks.length > 1 ? 'block' : 'none';
                }
            });
        };

        const init = () => {
            setupEventDelegation();

            if (addDishBtn) {
                addDishBtn.addEventListener('click', addNewDish);
            }

            updateDishNumbers();

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
        };

        init();
    };

    const initMenuConfigForms = (root = document) => {
        const forms = root.querySelectorAll('.menu_configurator_form');
        forms.forEach((form) => {
            if (form.dataset.menuConfigReady) {
                return;
            }
            form.dataset.menuConfigReady = 'true';
            initMenuConfigForm(form);
        });
    };

    window.initMenuConfigForms = initMenuConfigForms;
    initMenuConfigForms();
});