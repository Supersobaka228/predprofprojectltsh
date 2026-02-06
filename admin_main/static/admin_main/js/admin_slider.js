document.addEventListener('DOMContentLoaded', () => {
  const nav = document.querySelector('.admin_nav');
  const slider = document.querySelector('.admin_nav_slider');
  const buttons = document.querySelectorAll('.admin_nav_button');
  const views = document.querySelectorAll('.menu_app_view');

  if (!nav || !slider || buttons.length === 0) {
    return;
  }

  function moveSlider(button) {
    const buttonRect = button.getBoundingClientRect();
    const navRect = nav.getBoundingClientRect();
    const sliderHeight = slider.getBoundingClientRect().height;
    const top = buttonRect.top - navRect.top + (buttonRect.height - sliderHeight) / 2;
    slider.style.top = `${top}px`;
  }

  function openView(name) {
    views.forEach(view => {
      view.classList.toggle('menu_app_view--active', view.dataset.view === name);
    });
  }

  const initialButton = buttons[0];
  initialButton.classList.add('active');
  moveSlider(initialButton);
  openView(initialButton.dataset.view);

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      buttons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');

      moveSlider(button);
      openView(button.dataset.view);
    });
  });

  const openViewButtons = document.querySelectorAll('[data-open-view]');
  openViewButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const targetView = button.dataset.openView;
      if (targetView) {
        openView(targetView);
        const targetNavButton = Array.from(buttons)
          .find((navButton) => navButton.dataset.view === targetView);
        if (targetNavButton) {
          buttons.forEach(btn => btn.classList.remove('active'));
          targetNavButton.classList.add('active');
          moveSlider(targetNavButton);
        }
      }
    });
  });

  const closeAllProductPickers = () => {
    document.querySelectorAll('.chef_product_picker.is-open').forEach((picker) => {
      picker.classList.remove('is-open');
      const button = picker.querySelector('.chef_product_add');
      if (button) {
        button.setAttribute('aria-expanded', 'false');
      }
    });
  };

  document.addEventListener('click', (event) => {
    const addButton = event.target.closest('.chef_product_add');
    if (addButton) {
      event.preventDefault();
      event.stopPropagation();
      const picker = addButton.closest('.chef_product_picker');
      if (!picker) {
        return;
      }
      const isOpen = picker.classList.contains('is-open');
      closeAllProductPickers();
      picker.classList.toggle('is-open', !isOpen);
      addButton.setAttribute('aria-expanded', String(!isOpen));
      return;
    }

    const option = event.target.closest('.chef_product_option');
    if (option) {
      event.preventDefault();
      event.stopPropagation();
      const picker = option.closest('.chef_product_picker');
      if (!picker) {
        return;
      }
      const button = picker.querySelector('.chef_product_add');
      const input = picker.querySelector('.chef_product_input');
      const label = option.textContent.trim();
      if (button) {
        const textSpan = button.querySelector('span');
        if (textSpan) {
          textSpan.textContent = label;
        } else {
          button.textContent = label;
        }
        button.setAttribute('aria-expanded', 'false');
      }
      if (input) {
        input.value = option.dataset.value || label;
      }
      picker.classList.remove('is-open');
      return;
    }

    closeAllProductPickers();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeAllProductPickers();
    }
  });

  const orderForm = document.querySelector('#chefOrderForm');
  if (orderForm) {
    const orderBody = orderForm.querySelector('.chef_order_new_body');
    const addRowButton = orderForm.querySelector('.chef_order_new_add_btn');
    const rowTemplate = orderForm.querySelector('#chefOrderRowTemplate');
    let rowIndex = orderBody
      ? orderBody.querySelectorAll('.chef_order_new_row').length
      : 0;

    if (orderBody && addRowButton && rowTemplate) {
      addRowButton.addEventListener('click', () => {
        rowIndex += 1;
        const html = rowTemplate.innerHTML.replaceAll('__INDEX__', String(rowIndex));
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html.trim();
        const newRow = wrapper.firstElementChild;
        if (newRow) {
          orderBody.appendChild(newRow);
        }
      });

      orderBody.addEventListener('click', (event) => {
        const removeButton = event.target.closest('.chef_order_row_remove');
        if (!removeButton) {
          return;
        }
        const row = removeButton.closest('.chef_order_new_row');
        if (!row) {
          return;
        }
        const rows = orderBody.querySelectorAll('.chef_order_new_row');
        if (rows.length <= 1) {
          const input = row.querySelector('.chef_order_new_input');
          if (input) {
            input.value = '';
          }
          const hidden = row.querySelector('.chef_product_input');
          if (hidden) {
            hidden.value = '';
          }
          const button = row.querySelector('.chef_product_add span');
          if (button) {
            button.textContent = 'Выберите продукт';
          }
          return;
        }
        row.remove();
      });
    }
  }

  const dayMenuTabs = document.querySelectorAll('.day_menu_tab_input');
  const dayMenuBodies = document.querySelectorAll('.day_menu_table_body[data-meal]');

  const setDayMenu = (mealId) => {
    dayMenuBodies.forEach((body) => {
      body.classList.toggle('day_menu_table_body--active', body.dataset.meal === mealId);
    });
  };

  if (dayMenuTabs.length > 0 && dayMenuBodies.length > 0) {
    dayMenuTabs.forEach((tab) => {
      tab.addEventListener('change', () => {
        if (tab.checked) {
          setDayMenu(tab.id);
        }
      });
    });

    const activeTab = Array.from(dayMenuTabs).find((tab) => tab.checked) || dayMenuTabs[0];
    if (activeTab) {
      setDayMenu(activeTab.id);
    }
  }

  window.addEventListener('resize', () => {
    const activeButton = document.querySelector('.admin_nav_button.active') || buttons[0];
    moveSlider(activeButton);
  });

  const notifyWraps = document.querySelectorAll('.admin_notify_wrap');
  const sharedOverlay = document.querySelector('#adminNotifyOverlay');

  const closeAllNotifications = () => {
    notifyWraps.forEach((wrap) => {
      wrap.classList.remove('is-open');
    });
    if (sharedOverlay) {
      sharedOverlay.setAttribute('aria-hidden', 'true');
    }
  };

  if (notifyWraps.length > 0 && sharedOverlay) {
    notifyWraps.forEach((wrap) => {
      const button = wrap.querySelector('.admin_notify_button');

      if (!button) {
        return;
      }

      button.addEventListener('click', (event) => {
        event.stopPropagation();
        const willOpen = !wrap.classList.contains('is-open');
        closeAllNotifications();
        if (willOpen) {
          wrap.appendChild(sharedOverlay);
          wrap.classList.add('is-open');
          sharedOverlay.setAttribute('aria-hidden', 'false');
        }
      });
    });

    document.addEventListener('click', (event) => {
      const targetWrap = event.target instanceof Element
        ? event.target.closest('.admin_notify_wrap')
        : null;
      if (!targetWrap) {
        closeAllNotifications();
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeAllNotifications();
      }
    });
  }

  const classSelect = document.querySelector('.admin_menu_class_select');
  if (classSelect) {
    const classButton = classSelect.querySelector('.admin_menu_class_btn');
    const classLabel = classSelect.querySelector('.admin_menu_class_label');
    const classMenu = classSelect.querySelector('.admin_menu_class_menu');
    const classItems = classSelect.querySelectorAll('.admin_menu_class_item');

    const closeClassMenu = () => {
      classSelect.classList.remove('is-open');
      classButton.setAttribute('aria-expanded', 'false');
    };

    const toggleClassMenu = (event) => {
      event.stopPropagation();
      const isOpen = classSelect.classList.toggle('is-open');
      classButton.setAttribute('aria-expanded', String(isOpen));
    };

    if (classButton && classMenu && classLabel) {
      classButton.addEventListener('click', toggleClassMenu);

      classItems.forEach((item) => {
        item.addEventListener('click', () => {
          const value = item.dataset.value || '';
          const label = item.textContent.trim();
          classLabel.textContent = label;
          classButton.dataset.value = value;
          closeClassMenu();

          const changeEvent = new CustomEvent('classFilterChange', {
            detail: { value, label }
          });
          document.dispatchEvent(changeEvent);
        });
      });

      document.addEventListener('click', (event) => {
        if (!classSelect.contains(event.target)) {
          closeClassMenu();
        }
      });

      document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
          closeClassMenu();
        }
      });
    }
  }

  const titleSelects = document.querySelectorAll('.menu_config_title_select');
  if (titleSelects.length > 0) {
    const initTitleSelects = (root = document) => {
      const selects = root.querySelectorAll('.menu_config_title_select');
      const closeTitleMenus = () => {
        document.querySelectorAll('.menu_config_title_select').forEach((select) => {
          select.classList.remove('is-open');
          const button = select.querySelector('.menu_config_title_btn');
          if (button) {
            button.setAttribute('aria-expanded', 'false');
          }
        });
      };

      selects.forEach((select) => {
        if (select.dataset.titleSelectReady) {
          return;
        }
        select.dataset.titleSelectReady = 'true';

        const button = select.querySelector('.menu_config_title_btn');
        const label = select.querySelector('.menu_config_title_label');
        const items = select.querySelectorAll('.menu_config_title_item');
        const titleInput = select.closest('form')?.querySelector('input[name="category"]');

        if (!button || !label) {
          return;
        }

        if (titleInput && !titleInput.value && items.length > 0) {
          const first = items[0];
          label.textContent = first.textContent.trim();
          titleInput.value = first.dataset.value || '';
        }

        button.addEventListener('click', (event) => {
          event.stopPropagation();
          const isOpen = select.classList.contains('is-open');
          closeTitleMenus();
          select.classList.toggle('is-open', !isOpen);
          button.setAttribute('aria-expanded', String(!isOpen));
        });

        items.forEach((item) => {
          item.addEventListener('click', () => {
            label.textContent = item.textContent.trim();
            if (titleInput) {
              titleInput.value = item.dataset.value || '';
            }
            closeTitleMenus();
          });
        });
      });

      document.addEventListener('click', () => {
        closeTitleMenus();
      });

      document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
          closeTitleMenus();
        }
      });
    };

    window.initMenuTitleSelects = initTitleSelects;
    initTitleSelects();
  }
});
