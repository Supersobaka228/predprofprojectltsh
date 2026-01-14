document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("overlay");
  const sheet = document.getElementById("sheet");
  const closeBtn = document.getElementById("closeSheet");
  const openButtons = document.querySelectorAll(".openSheet");

  // Функция блокировки прокрутки body при открытом листе
  function lockBody(lock) {
    if (lock) {
      const scrollY = window.scrollY || document.documentElement.scrollTop;
      document.body.style.position = "fixed";
      document.body.style.top = `-${scrollY}px`;
      document.body.style.width = "100%";
      document.body.style.overflow = "hidden";
      document.body.dataset.scrollY = scrollY;
    } else {
      const scrollY = document.body.dataset.scrollY ? parseInt(document.body.dataset.scrollY) : 0;
      document.body.style.position = "";
      document.body.style.top = "";
      document.body.style.width = "";
      document.body.style.overflow = "";
      document.body.removeAttribute("data-scrollY");
      window.scrollTo(0, scrollY);
    }
  }

  // Заполнение шторки данными
  function fillSheet(button) {
    const time = button.getAttribute('data-time');
    const name = button.getAttribute('data-name');
    const price = button.getAttribute('data-price');
    const icon = button.getAttribute('data-icon');

    // Парсим JSON строки (в вашем шаблоне они как строки, а не JSON)
    const maxDesStr = button.getAttribute('data-max-des');
    const allergensStr = button.getAttribute('data-allergens');

    let maxDes = [];
    let allergens = [];

    try {
      // Пытаемся распарсить как JSON
      maxDes = JSON.parse(maxDesStr);
    } catch {
      // Если не JSON, то разбиваем по ||
      maxDes = maxDesStr ? maxDesStr.split('||') : [];
    }

    try {
      allergens = JSON.parse(allergensStr);
    } catch {
      allergens = allergensStr ? allergensStr.split('||') : [];
    }

    // Заполняем элементы
    document.getElementById('sheet-time').textContent = time || '9:10-9:30';
    document.getElementById('sheet-name').textContent = name || 'Блюдо';
    document.getElementById('sheet-price').textContent = (price || '170') + '₽';

    // Изображение
    const sheetImage = document.querySelector('.sheet_main_img');
    if (sheetImage && icon) {
      sheetImage.src = icon;
    }

    // Состав
    const compositionList = document.getElementById('sheet-composition');
    if (compositionList) {
      compositionList.innerHTML = '';
      maxDes.forEach(desc => {
        const li = document.createElement('li');
        li.className = 'sheet_text';
        li.textContent = desc;
        compositionList.appendChild(li);
      });
    }

    // Аллергены
    const allergensList = document.getElementById('sheet-allergens');
    if (allergensList) {
      allergensList.innerHTML = '';
      allergens.forEach(allergen => {
        const li = document.createElement('li');
        li.className = 'sheet_text';
        li.textContent = allergen;
        allergensList.appendChild(li);
      });
    }
  }

  // Открытие листа
  function openSheet(button) {
    fillSheet(button);

    // Показываем элементы
    overlay.style.display = 'block';
    setTimeout(() => {
      overlay.classList.add("active");
      sheet.classList.add("active");
    }, 10);

    lockBody(true);
  }

  // Закрытие
  function closeSheet() {
    overlay.classList.remove("active");
    sheet.classList.remove("active");

    setTimeout(() => {
      overlay.style.display = 'none';
    }, 300); // Ждем завершения анимации

    lockBody(false);
    sheet.style.transform = "";
  }

  // Навешиваем обработчики на кнопки открытия
  openButtons.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      openSheet(btn);
    });
  });

  // Закрытие по кнопке крестика
  closeBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    closeSheet();
  });

  // Закрытие при клике по фону оверлея
  overlay.addEventListener("click", e => {
    if (e.target === overlay) {
      closeSheet();
    }
  });

  // Закрытие по клавише ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && overlay.classList.contains('active')) {
      closeSheet();
    }
  });

  /* ===== SWIPE DOWN для мобильных ===== */
  let startY = 0;
  let currentY = 0;
  let isDragging = false;

  sheet.addEventListener("touchstart", e => {
    startY = e.touches[0].clientY;
    isDragging = true;
  });

  sheet.addEventListener("touchmove", e => {
    if (!isDragging) return;
    currentY = e.touches[0].clientY - startY;
    if (currentY > 0) {
      sheet.style.transition = "none";
      sheet.style.transform = `translateY(${currentY}px)`;
    }
  });

  sheet.addEventListener("touchend", () => {
    isDragging = false;
    sheet.style.transition = "";
    if (currentY > 120) {
      closeSheet();
    } else {
      sheet.style.transform = "";
    }
    currentY = 0;
  });
});
