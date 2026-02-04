document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('.menu_configurator_form');
  if (forms.length === 0) {
    return;
  }

  const closeAllPickers = () => {
    document.querySelectorAll('.menu_config_allergen_picker.is-open, .menu_config_ingredient_picker.is-open')
      .forEach((picker) => {
        picker.classList.remove('is-open');
        const button = picker.querySelector('.menu_config_add');
        if (button) {
          button.setAttribute('aria-expanded', 'false');
        }
      });
  };

  const getDishIndex = (element) => {
    const dishBlock = element.closest('.dish-block');
    if (!dishBlock) {
      return '0';
    }
    return dishBlock.getAttribute('data-dish-index') || '0';
  };

  const buildChip = ({ label, id, type, dishIndex }) => {
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
      chip.appendChild(gramsInput);
    }

    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'menu_config_chip_button';
    removeButton.setAttribute('aria-label', `Удалить ${type === 'ingredient' ? 'ингредиент' : 'аллерген'} ${label}`);

    const removeIcon = document.createElement('img');
    removeIcon.src = 'resources/delete.svg';
    removeIcon.alt = '';
    removeButton.appendChild(removeIcon);

    chip.appendChild(removeButton);
    return chip;
  };

  forms.forEach((form) => {
    form.addEventListener('click', (event) => {
      const addButton = event.target.closest('.menu_config_add');
      if (addButton) {
        event.preventDefault();
        event.stopPropagation();
        const picker = addButton.closest('.menu_config_allergen_picker, .menu_config_ingredient_picker');
        if (!picker) {
          return;
        }
        const isOpen = picker.classList.contains('is-open');
        closeAllPickers();
        picker.classList.toggle('is-open', !isOpen);
        addButton.setAttribute('aria-expanded', String(!isOpen));
        return;
      }

      const allergenOption = event.target.closest('.menu_config_allergen_option');
      if (allergenOption) {
        event.preventDefault();
        const dishRow = allergenOption.closest('.menu_config_dish_row');
        const allergensWrap = dishRow ? dishRow.querySelector('.menu_config_allergens') : null;
        if (!allergensWrap) {
          return;
        }

        const dishIndex = getDishIndex(allergenOption);
        const allergenId = allergenOption.dataset.allergenId || allergenOption.textContent.trim();
        const allergenLabel = allergenOption.textContent.trim();

        const existing = allergensWrap.querySelector(`[data-item-id="${allergenId}"][data-item-type="allergen"]`);
        if (!existing) {
          const chip = buildChip({ label: allergenLabel, id: allergenId, type: 'allergen', dishIndex });
          allergensWrap.appendChild(chip);

          const hiddenInput = document.createElement('input');
          hiddenInput.type = 'hidden';
          hiddenInput.name = `allergens_${dishIndex}[]`;
          hiddenInput.value = allergenId;
          hiddenInput.dataset.itemId = allergenId;
          hiddenInput.dataset.itemType = 'allergen';
          allergensWrap.appendChild(hiddenInput);
        }

        closeAllPickers();
        return;
      }

      const ingredientOption = event.target.closest('.menu_config_ingredient_option');
      if (ingredientOption) {
        event.preventDefault();
        const dishRow = ingredientOption.closest('.menu_config_dish_row');
        const ingredientsWrap = dishRow ? dishRow.querySelector('.menu_config_ingredients') : null;
        if (!ingredientsWrap) {
          return;
        }

        const dishIndex = getDishIndex(ingredientOption);
        const ingredientId = ingredientOption.dataset.ingredientId || ingredientOption.textContent.trim();
        const ingredientLabel = ingredientOption.textContent.trim();

        const existing = ingredientsWrap.querySelector(`[data-item-id="${ingredientId}"][data-item-type="ingredient"]`);
        if (!existing) {
          const chip = buildChip({ label: ingredientLabel, id: ingredientId, type: 'ingredient', dishIndex });
          ingredientsWrap.appendChild(chip);

          const hiddenInput = document.createElement('input');
          hiddenInput.type = 'hidden';
          hiddenInput.name = `ingredients_${dishIndex}[]`;
          hiddenInput.value = ingredientId;
          hiddenInput.dataset.itemId = ingredientId;
          hiddenInput.dataset.itemType = 'ingredient';
          ingredientsWrap.appendChild(hiddenInput);
        }

        closeAllPickers();
      }
    });

    form.addEventListener('click', (event) => {
      const removeButton = event.target.closest('.menu_config_chip_button');
      if (!removeButton) {
        return;
      }
      event.preventDefault();
      const chip = removeButton.closest('.menu_config_chip');
      const wrap = chip ? chip.parentElement : null;
      const itemId = chip ? chip.dataset.itemId : null;
      const itemType = chip ? chip.dataset.itemType : null;

      if (chip && wrap) {
        chip.remove();
        if (itemId && itemType) {
          const hiddenInput = wrap.querySelector(`input[type="hidden"][data-item-id="${itemId}"][data-item-type="${itemType}"]`);
          if (hiddenInput) {
            hiddenInput.remove();
          }
        }
      }
    });
  });

  document.addEventListener('click', () => {
    closeAllPickers();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeAllPickers();
    }
  });
});
