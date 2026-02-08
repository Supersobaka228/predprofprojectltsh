document.addEventListener('DOMContentLoaded', () => {
  const dataTag = document.getElementById('menu-prefill-data');
  const formsContainer = document.getElementById('menu-config-forms');
  const formTemplate = document.getElementById('menu-config-template');
  const dayInput = document.getElementById('day_input_value');
  const deleteIconSrc = formsContainer?.dataset?.deleteIcon || '/static/icon/delete.svg';

  if (!formsContainer || !formTemplate) {
    return;
  }

  let menuData = { days: {} };
  if (dataTag && dataTag.textContent) {
    try {
      menuData = JSON.parse(dataTag.textContent);
    } catch (err) {
      console.warn('Failed to parse menu prefill data', err);
    }
  }

  const categoryLabelMap = {
    breakfast: 'Завтрак',
    lunch: 'Обед',
  };

  const buildChip = ({ label, id, type, dishIndex, grams }) => {
    const chip = document.createElement('span');
    chip.className = 'menu_config_chip';
    chip.dataset.itemId = id;
    chip.dataset.itemType = type;

    const chipText = document.createElement('span');
    chipText.textContent = label;
    chip.appendChild(chipText);

    if (type === 'ingredient') {
      const gramsInput = document.createElement('input');
      gramsInput.type = 'number';
      gramsInput.min = '1';
      gramsInput.placeholder = 'г';
      gramsInput.className = 'menu_config_chip_input';
      gramsInput.name = `ingredients_grams_${dishIndex}[]`;
      gramsInput.dataset.ingredientId = id;
      gramsInput.value = grams ? String(grams) : '';
      chip.appendChild(gramsInput);
    }

    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'menu_config_chip_button';
    removeButton.setAttribute('aria-label', `Удалить ${type === 'ingredient' ? 'ингредиент' : 'аллерген'} ${label}`);

    const removeIcon = document.createElement('img');
    removeIcon.src = deleteIconSrc;
    removeIcon.alt = '';
    removeButton.appendChild(removeIcon);

    chip.appendChild(removeButton);
    return chip;
  };

  const clearDishSelections = (dishBlock) => {
    const allergensWrap = dishBlock.querySelector('.menu_config_allergens');
    const ingredientsWrap = dishBlock.querySelector('.menu_config_ingredients');
    if (allergensWrap) {
      allergensWrap.innerHTML = '';
    }
    if (ingredientsWrap) {
      ingredientsWrap.innerHTML = '';
    }
  };

  const ensureDishIndex = (dishBlock, index) => {
    dishBlock.setAttribute('data-dish-index', String(index));
    const numberSpan = dishBlock.querySelector('.dish-number');
    if (numberSpan) {
      numberSpan.textContent = String(index + 1);
    }

    dishBlock.querySelectorAll('input[name^="allergens_"]').forEach((input) => {
      input.name = `allergens_${index}[]`;
    });

    dishBlock.querySelectorAll('input[name^="ingredients_"]').forEach((input) => {
      if (input.type === 'hidden') {
        input.name = `ingredients_${index}[]`;
      }
    });

    dishBlock.querySelectorAll('input[name^="ingredients_grams_"]').forEach((input) => {
      input.name = `ingredients_grams_${index}[]`;
    });
  };

  const fillDishBlock = (dishBlock, meal, index) => {
    ensureDishIndex(dishBlock, index);

    const nameInput = dishBlock.querySelector('input[name="dish_name[]"]');
    const weightInput = dishBlock.querySelector('input[name="dish_weight[]"]');
    const kcalInput = dishBlock.querySelector('input[name="dish_kcal[]"]');

    if (nameInput) {
      nameInput.value = meal.name || '';
    }
    if (weightInput) {
      weightInput.value = meal.weight != null ? String(meal.weight) : '';
    }
    if (kcalInput) {
      kcalInput.value = meal.calories != null ? String(meal.calories) : '';
    }

    clearDishSelections(dishBlock);

    const allergensWrap = dishBlock.querySelector('.menu_config_allergens');
    if (allergensWrap && Array.isArray(meal.allergens)) {
      meal.allergens.forEach((allergen) => {
        const chip = buildChip({
          label: allergen.name,
          id: allergen.code,
          type: 'allergen',
          dishIndex: index,
        });
        allergensWrap.appendChild(chip);

        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = `allergens_${index}[]`;
        hiddenInput.value = allergen.code;
        hiddenInput.dataset.itemId = allergen.code;
        hiddenInput.dataset.itemType = 'allergen';
        allergensWrap.appendChild(hiddenInput);
      });
    }

    const ingredientsWrap = dishBlock.querySelector('.menu_config_ingredients');
    if (ingredientsWrap && Array.isArray(meal.ingredients)) {
      meal.ingredients.forEach((ingredient) => {
        const chip = buildChip({
          label: ingredient.name,
          id: ingredient.code,
          type: 'ingredient',
          dishIndex: index,
          grams: ingredient.grams,
        });
        ingredientsWrap.appendChild(chip);

        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = `ingredients_${index}[]`;
        hiddenInput.value = ingredient.code;
        hiddenInput.dataset.itemId = ingredient.code;
        hiddenInput.dataset.itemType = 'ingredient';
        ingredientsWrap.appendChild(hiddenInput);
      });
    }
  };

  const createForm = (dayValue) => {
    const fragment = formTemplate.content.cloneNode(true);
    const form = fragment.querySelector('form.menu_configurator_form');
    if (!form) {
      return null;
    }

    const dayField = form.querySelector('.menu_config_day_value');
    if (dayField) {
      dayField.value = dayValue || '';
    }

    return form;
  };

  const renderFormsForDay = (dayValue) => {
    formsContainer.innerHTML = '';

    const dayKey = dayValue ? String(dayValue) : '';
    const dayItems = (menuData.days && dayKey && menuData.days[dayKey]) ? menuData.days[dayKey] : [];

    if (!dayItems || dayItems.length === 0) {
      const emptyForm = createForm(dayValue);
      if (emptyForm) {
        formsContainer.appendChild(emptyForm);
      }
    } else {
      dayItems.forEach((item) => {
        const form = createForm(dayValue);
        if (!form) {
          return;
        }

        const categoryInput = form.querySelector('input[name="category"]');
        if (categoryInput) {
          categoryInput.value = item.category || '';
        }

        const titleLabel = form.querySelector('.menu_config_title_label');
        if (titleLabel) {
          titleLabel.textContent = categoryLabelMap[item.category] || item.category || 'Завтрак';
        }

        const timeStart = form.querySelector('input[name="time_start"]');
        const timeEnd = form.querySelector('input[name="time_end"]');
        const priceInput = form.querySelector('input[name="price"]');

        if (timeStart) {
          timeStart.value = item.time_start || '';
        }
        if (timeEnd) {
          timeEnd.value = item.time_end || '';
        }
        if (priceInput) {
          priceInput.value = item.price != null ? String(item.price) : '';
        }

        const dishContainer = form.querySelector('[data-dishes-container]');
        const dishBlocks = dishContainer ? dishContainer.querySelectorAll('.dish-block') : [];

        if (dishContainer && Array.isArray(item.meals) && item.meals.length > 0) {
          const firstBlock = dishBlocks[0];
          if (firstBlock) {
            fillDishBlock(firstBlock, item.meals[0], 0);
          }

          for (let i = 1; i < item.meals.length; i += 1) {
            const clone = firstBlock.cloneNode(true);
            fillDishBlock(clone, item.meals[i], i);
            dishContainer.appendChild(clone);
          }
        }

        formsContainer.appendChild(form);
      });
    }

    if (window.initMenuTitleSelects) {
      window.initMenuTitleSelects(formsContainer);
    }

    if (window.initMenuConfigForms) {
      window.initMenuConfigForms(formsContainer);
    }

    if (window.initMenuPickers) {
      window.initMenuPickers(formsContainer);
    }
  };

  const initialDay = dayInput && dayInput.value ? dayInput.value : '1';
  renderFormsForDay(initialDay);

  document.addEventListener('menuDayChange', (event) => {
    const dayValue = event.detail && event.detail.day ? String(event.detail.day) : '';
    if (!dayValue) {
      return;
    }
    renderFormsForDay(dayValue);
  });
});

