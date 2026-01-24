document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("overlay");
  const sheet = document.getElementById("sheet");
  const closeBtn = document.getElementById("closeSheet");
  const openButtons = document.querySelectorAll(".openSheet");
  const rateOverlay = document.getElementById("rateOverlay");
  const openRateBtn = document.getElementById("openRate");
  const rateCancel = document.getElementById("rateCancel");
  let currentItemData = {};

  function splitDataset(value) {
    if (!value) return [];
    return value
      .split('||')
      .map(s => (s || '').trim())
      .filter(Boolean);
  }

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? '';
  }

  function setValue(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value ?? '';
  }

  function fillList(listEl, items, tagName = 'li') {
    if (!listEl) return;
    listEl.innerHTML = '';
    items.forEach(item => {
      const li = document.createElement(tagName);
      li.textContent = item;
      listEl.appendChild(li);
    });
  }

  function openSheetWithData(e) {
    e.preventDefault();

    const button = e.currentTarget;

    currentItemData = {
      date: button.getAttribute('data-date'),
      item: button.getAttribute('data-item'),
      name: button.getAttribute('data-name'),
      categoryLabel: button.getAttribute('data-category'),
      time: button.getAttribute('data-time'),
      price: button.getAttribute('data-price'),
      icon: button.getAttribute('data-icon'),
      maxDes: button.getAttribute('data-max-des'),
      allergens: button.getAttribute('data-allergens')
    };

    openSheet();
  }

  function lockBody(lock) {
    if (lock) {
      const scrollY = window.scrollY || document.documentElement.scrollTop;
      document.body.style.position = "fixed";
      document.body.style.top = `-${scrollY}px`;
      document.body.style.left = "0";
      document.body.style.right = "0";
      document.body.dataset.scrollY = scrollY;
    } else {
      const scrollY = document.body.dataset.scrollY ? parseInt(document.body.dataset.scrollY) : 0;
      document.body.style.position = "";
      document.body.style.top = "";
      document.body.style.left = "";
      document.body.style.right = "";
      document.body.removeAttribute("data-scrollY");
      window.scrollTo(0, scrollY);
    }
  }

  function openSheet() {
    const compositionList = document.getElementById('sheet-composition');
    const allergensList = document.getElementById('sheet-allergens');

    // Заполняем UI
    setText('sheet-time', currentItemData.time || '');
    setText('sheet-name', currentItemData.categoryLabel || currentItemData.name || '');
    setText('sheet-price', currentItemData.price ? `${currentItemData.price}₽` : '');

    const sheetImage = document.getElementById('sheet-image');
    if (sheetImage && currentItemData.icon) {
      sheetImage.src = currentItemData.icon;
    }

    // Состав: используем data-max-des (строки description) — это "Состав" для sheet
    fillList(compositionList, splitDataset(currentItemData.maxDes), 'li');

    // Аллергены
    fillList(allergensList, splitDataset(currentItemData.allergens), 'li');

    overlay.classList.add("active");

    // Hidden поля заказа
    // name — оставляем как раньше (у вас это category код), чтобы не ломать обработчик заказа
    setValue('itemDateField2', currentItemData.name);
    setValue('itemDateField3', currentItemData.time);
    setValue('itemDateField4', currentItemData.price);
    setValue('itemDateField5', currentItemData.date);

    lockBody(true);
  }

  function closeSheet() {
    overlay.classList.remove("active");
    lockBody(false);
    sheet.style.transform = "";
  }

  // Навешиваем обработчики на кнопки открытия
  openButtons.forEach(btn => {
    btn.addEventListener("click", openSheetWithData);
  });

  // Закрытие по кнопке крестика
  closeBtn.addEventListener("click", closeSheet);

  // Закрытие при клике по фону оверлея
  overlay.addEventListener("click", e => {
    if (isRateOpen) return;
    if (e.target === overlay) closeSheet();
  });

  /* ===== SWIPE DOWN для мобильных ===== */
  let startY = 0;
  let currentY = 0;
  let isDragging = false;

  sheet.addEventListener("touchstart", e => {
    if (isRateOpen) return;
    startY = e.touches[0].clientY;
    isDragging = true;
  });

  sheet.addEventListener("touchmove", e => {
    if (!isDragging || isRateOpen) return;
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

  let isRateOpen = false;

  function openRate(e) {
    e.preventDefault();
    isRateOpen = true;
    rateOverlay.classList.add("active");



    // Заполняем поля формы данными

    setValue('itemDateField', currentItemData.date || '');
    setValue('itemCategoryField', currentItemData.item || '');

    // блокируем взаимодействие с sheet
    sheet.style.touchAction = "none";
  }

  function closeRate() {
    isRateOpen = false;
    rateOverlay.classList.remove("active");
    sheet.style.touchAction = "";
  }

  /* Открытие */
  openRateBtn.addEventListener("click", (e) => {
    e.preventDefault();
    openRate(e);
  });

  /* Закрытие по кнопке */
  rateCancel.addEventListener("click", closeRate);

  /* Закрытие по фону */
  rateOverlay.addEventListener("click", e => {
    if (e.target === rateOverlay) {
      closeRate();
    }
  });
});