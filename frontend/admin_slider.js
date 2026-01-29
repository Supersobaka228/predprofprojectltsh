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

  window.addEventListener('resize', () => {
    const activeButton = document.querySelector('.admin_nav_button.active') || buttons[0];
    moveSlider(activeButton);
  });

  const notifyWraps = document.querySelectorAll('.admin_notify_wrap');

  const closeAllNotifications = () => {
    notifyWraps.forEach((wrap) => {
      const overlay = wrap.querySelector('.admin_notify_overlay');
      wrap.classList.remove('is-open');
      if (overlay) {
        overlay.setAttribute('aria-hidden', 'true');
      }
    });
  };

  if (notifyWraps.length > 0) {
    notifyWraps.forEach((wrap) => {
      const button = wrap.querySelector('.admin_notify_button');
      const overlay = wrap.querySelector('.admin_notify_overlay');

      if (!button || !overlay) {
        return;
      }

      button.addEventListener('click', (event) => {
        event.stopPropagation();
        const willOpen = !wrap.classList.contains('is-open');
        closeAllNotifications();
        if (willOpen) {
          wrap.classList.add('is-open');
          overlay.setAttribute('aria-hidden', 'false');
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
});
