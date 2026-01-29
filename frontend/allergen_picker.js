document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('.menu_configurator_form');
  if (!form) {
    return;
  }

  const closeAllPickers = () => {
    form.querySelectorAll('.menu_config_allergen_picker.is-open').forEach((picker) => {
      picker.classList.remove('is-open');
      const button = picker.querySelector('.menu_config_add');
      if (button) {
        button.setAttribute('aria-expanded', 'false');
      }
    });
  };

  form.addEventListener('click', (event) => {
    const addButton = event.target.closest('.menu_config_add');
    if (addButton) {
      event.preventDefault();
      event.stopPropagation();
      const picker = addButton.closest('.menu_config_allergen_picker');
      if (!picker) {
        return;
      }
      const isOpen = picker.classList.contains('is-open');
      closeAllPickers();
      picker.classList.toggle('is-open', !isOpen);
      addButton.setAttribute('aria-expanded', String(!isOpen));
      return;
    }

    const option = event.target.closest('.menu_config_allergen_option');
    if (option) {
      event.preventDefault();
      const picker = option.closest('.menu_config_allergen_picker');
      const dishRow = option.closest('.menu_config_dish_row');
      const allergensWrap = dishRow ? dishRow.querySelector('.menu_config_allergens') : null;
      if (!allergensWrap) {
        return;
      }

      const allergenId = option.dataset.allergenId || option.textContent.trim();
      const allergenLabel = option.textContent.trim();

      const existing = allergensWrap.querySelector(`[data-allergen-id="${allergenId}"]`);
      if (!existing) {
        const chip = document.createElement('span');
        chip.className = 'menu_config_chip';
        chip.dataset.allergenId = allergenId;

        const chipText = document.createElement('span');
        chipText.textContent = allergenLabel;

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'menu_config_chip_button';
        removeButton.setAttribute('aria-label', `Удалить аллерген ${allergenLabel}`);

        const removeIcon = document.createElement('img');
        removeIcon.src = 'resources/delete.svg';
        removeIcon.alt = '';
        removeButton.appendChild(removeIcon);

        chip.appendChild(chipText);
        chip.appendChild(removeButton);
        allergensWrap.appendChild(chip);

        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'allergens[]';
        hiddenInput.value = allergenId;
        hiddenInput.dataset.allergenId = allergenId;
        allergensWrap.appendChild(hiddenInput);
      }

      if (picker) {
        picker.classList.remove('is-open');
        const button = picker.querySelector('.menu_config_add');
        if (button) {
          button.setAttribute('aria-expanded', 'false');
        }
      }
    }
  });

  document.addEventListener('click', () => {
    closeAllPickers();
  });

  form.addEventListener('click', (event) => {
    const removeButton = event.target.closest('.menu_config_chip_button');
    if (!removeButton) {
        return;
    }
    event.preventDefault();
    const chip = removeButton.closest('.menu_config_chip');
    const allergensWrap = chip ? chip.parentElement : null;
    const allergenId = chip ? chip.dataset.allergenId : null;

    if (chip && allergensWrap) {
      chip.remove();
      if (allergenId) {
        const hiddenInput = allergensWrap.querySelector(`input[type="hidden"][data-allergen-id="${allergenId}"]`);
        if (hiddenInput) {
          hiddenInput.remove();
        }
      }
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeAllPickers();
    }
  });
});
