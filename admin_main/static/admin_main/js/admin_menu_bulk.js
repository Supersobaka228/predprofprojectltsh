document.addEventListener('DOMContentLoaded', () => {
  const formsContainer = document.getElementById('menu-config-forms');
  const saveAllButton = document.querySelector('.menu_config_save_all');

  if (!formsContainer || !saveAllButton) {
    return;
  }

  const categoryMap = {
    'Завтрак': 'breakfast',
    'Обед': 'lunch',
  };

  const clearDishBlock = (dishBlock) => {
    const nameInput = dishBlock.querySelector('input[name="dish_name[]"]');
    const weightInput = dishBlock.querySelector('input[name="dish_weight[]"]');
    const kcalInput = dishBlock.querySelector('input[name="dish_kcal[]"]');

    if (nameInput) {
      nameInput.value = '';
    }
    if (weightInput) {
      weightInput.value = '';
    }
    if (kcalInput) {
      kcalInput.value = '';
    }

    const allergensWrap = dishBlock.querySelector('.menu_config_allergens');
    const ingredientsWrap = dishBlock.querySelector('.menu_config_ingredients');
    if (allergensWrap) {
      allergensWrap.innerHTML = '';
    }
    if (ingredientsWrap) {
      ingredientsWrap.innerHTML = '';
    }
  };

  const resetForm = (form) => {
    const dishBlocks = form.querySelectorAll('.dish-block');
    if (dishBlocks.length > 0) {
      const first = dishBlocks[0];
      clearDishBlock(first);
      dishBlocks.forEach((block, index) => {
        if (index === 0) {
          return;
        }
        block.remove();
      });

      first.setAttribute('data-dish-index', '0');
      const dishNumber = first.querySelector('.dish-number');
      if (dishNumber) {
        dishNumber.textContent = '1';
      }
    }

    form.querySelectorAll('input[name="time_start"], input[name="time_end"], input[name="price"]').forEach((input) => {
      input.value = '';
    });

    const categoryInput = form.querySelector('input[name="category"]');
    if (categoryInput) {
      categoryInput.value = '';
    }

    const titleLabel = form.querySelector('.menu_config_title_label');
    if (titleLabel) {
      titleLabel.textContent = 'Завтрак';
    }
  };

  const hasAnyDish = (form) => {
    const dishNames = Array.from(form.querySelectorAll('input[name="dish_name[]"]'));
    return dishNames.some((input) => input.value.trim());
  };

  const validateForm = (form) => {
    const dishNames = Array.from(form.querySelectorAll('input[name="dish_name[]"]'));
    let hasEmpty = false;

    dishNames.forEach((input) => {
      if (!input.value.trim()) {
        hasEmpty = true;
        input.style.borderColor = 'red';
      } else {
        input.style.borderColor = '';
      }
    });

    if (hasEmpty) {
      return 'Пожалуйста, заполните названия всех блюд!';
    }

    return '';
  };

  formsContainer.addEventListener('click', (event) => {
    const cancelButton = event.target.closest('.menu_config_btn--cancel');
    if (!cancelButton) {
      return;
    }
    event.preventDefault();

    const form = cancelButton.closest('.menu_configurator_form');
    if (!form) {
      return;
    }

    const forms = formsContainer.querySelectorAll('.menu_configurator_form');
    if (forms.length > 1) {
      form.remove();
    } else {
      resetForm(form);
    }
  });

  saveAllButton.addEventListener('click', async (event) => {
    event.preventDefault();

    const forms = Array.from(formsContainer.querySelectorAll('.menu_configurator_form'));
    if (forms.length === 0) {
      return;
    }

    const formsToSubmit = forms.filter((form) => hasAnyDish(form));
    if (formsToSubmit.length === 0) {
      alert('Нет заполненных меню для сохранения.');
      return;
    }

    for (const form of formsToSubmit) {
      const validationMessage = validateForm(form);
      if (validationMessage) {
        alert(validationMessage);
        return;
      }
    }

    saveAllButton.disabled = true;

    try {
      for (const form of formsToSubmit) {
        const categoryInput = form.querySelector('input[name="category"]');
        const titleLabel = form.querySelector('.menu_config_title_label');
        if (categoryInput && !categoryInput.value && titleLabel) {
          const labelValue = titleLabel.textContent.trim();
          categoryInput.value = categoryMap[labelValue] || '';
        }

        const formData = new FormData(form);
        const actionUrl = form.getAttribute('action') || window.location.href;

        const response = await fetch(actionUrl, {
          method: 'POST',
          body: formData,
          credentials: 'same-origin',
        });

        if (!response.ok) {
          throw new Error('Save failed');
        }
      }

      window.location.href = window.location.href;
    } catch (error) {
      alert('Не удалось сохранить меню. Попробуйте ещё раз.');
    } finally {
      saveAllButton.disabled = false;
    }
  });
});

