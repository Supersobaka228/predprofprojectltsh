document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("overlay");
  const sheet = document.getElementById("sheet");
  const closeBtn = document.getElementById("closeSheet");
  const openButtons = document.querySelectorAll(".openSheet");
  const rateOverlay = document.getElementById("rateOverlay");
  const openRateBtn = document.getElementById("openRate");
  const rateCancel = document.getElementById("rateCancel");
   const paymentOverlay = document.getElementById("paymentOverlay");
  const openPaymentBtn = document.getElementById("openPayment");
  const paymentClose = document.getElementById("paymentClose");
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
    console.log(123);
    currentItemData = {
      date: button.getAttribute('data-date'),
      item: button.getAttribute('data-item'),
      name: button.getAttribute('data-name'),
      categoryLabel: button.getAttribute('data-category'),
      time: button.getAttribute('data-time'),
      price: button.getAttribute('data-price'),
      icon: button.getAttribute('data-icon'),
      maxDes: button.getAttribute('data-max-des'),
      composition: button.getAttribute('data-composition'),
      ratingAvg: button.getAttribute('data-rating-avg'),
      ratingCount: button.getAttribute('data-rating-count'),
      allergens: button.getAttribute('data-allergens'),
      orderStatus: button.getAttribute('data-order-status')
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

  function filterReviewsForItem(itemId) {
    const reviewsContainer = document.getElementById('reviews-container');
    if (!reviewsContainer) return;

    const emptyEl = document.getElementById('sheet-review-empty');
    const reviews = Array.from(reviewsContainer.querySelectorAll('.sheet-review'));

    let shown = 0;
    reviews.forEach(r => {
      const reviewItemId = r.getAttribute('data-review-item-id');
      // itemId и reviewItemId должны совпасть как строки
      const match = itemId && reviewItemId && String(reviewItemId) === String(itemId);
      r.style.display = match ? '' : 'none';
      if (match) shown += 1;
    });

    if (emptyEl) {
      emptyEl.style.display = shown === 0 ? '' : 'none';
    }
  }

  function ensureRatingMarkup(starsBox) {
    if (!starsBox) return;
    if (starsBox.querySelector('.rating-stars-bg')) return;

    const starSrc = '../../static/menu/icon/Star 1.svg';
    const bg = document.createElement('div');
    bg.className = 'rating-stars-layer rating-stars-bg';

    const fill = document.createElement('div');
    fill.className = 'rating-stars-layer rating-stars-fill';

    for (let i = 0; i < 5; i++) {
      const imgBg = document.createElement('img');
      imgBg.src = starSrc;
      imgBg.alt = '';
      bg.appendChild(imgBg);

      const imgFill = document.createElement('img');
      imgFill.src = starSrc;
      imgFill.alt = '';
      fill.appendChild(imgFill);
    }

    starsBox.appendChild(bg);
    starsBox.appendChild(fill);
  }

  function setRating(value) {
    const starsBoxes = Array.from(document.querySelectorAll('.sheet-rating-stars-box'));
    const valueEls = Array.from(document.querySelectorAll('.sheet-rating-value'));
    const rating = Number(value);
    const safeRating = Number.isFinite(rating) ? Math.max(0, Math.min(5, rating)) : 0;

    const display = safeRating.toFixed(1).replace('.', ',');

    starsBoxes.forEach(starsBox => {
      ensureRatingMarkup(starsBox);
      const percent = (safeRating / 5) * 100;
      starsBox.style.setProperty('--rating-percent', `${percent}%`);

      const container = starsBox.closest('.sheet-rating-stars');
      if (container) {
        container.setAttribute('aria-label', `Рейтинг ${display} из 5`);
      }
      starsBox.setAttribute('aria-label', `Рейтинг ${display} из 5`);
    });

    valueEls.forEach(valueEl => {
      valueEl.textContent = `${display}/5`;
    });
  }

  function applyOrderButtonState(status) {
    const orderBtn = document.querySelector('.sheet_order_btn');
    if (!orderBtn) return;
    const titleEl = orderBtn.querySelector('.sheet_title');
    const textEl = orderBtn.querySelector('.sheet_text');

    orderBtn.disabled = false;
    orderBtn.dataset.orderStatus = status || '';

    if (status === 'confirmed') {
      if (titleEl) titleEl.textContent = 'Получено';
      if (textEl) textEl.textContent = '';
      orderBtn.disabled = true;
      return;
    }

    if (status === 'ordered') {
      if (titleEl) titleEl.textContent = 'Подтвердить получение';
      if (textEl) textEl.textContent = '';
      return;
    }

    if (titleEl) titleEl.textContent = 'Заказать';
    if (textEl) textEl.textContent = '(для дальнейшего получения на кассе)';
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

    // Состав: берём из data-composition
    fillList(compositionList, splitDataset(currentItemData.composition), 'li');

    // Аллергены
    fillList(allergensList, splitDataset(currentItemData.allergens), 'li');

    // Средний рейтинг
    setRating(currentItemData.ratingAvg);

    // Фильтруем отзывы под выбранный MenuItem
    filterReviewsForItem(currentItemData.item);

    overlay.classList.add("active");

    // Hidden поля заказа
    // name — оставляем как раньше (у вас это category код), чтобы не ломать обработчик заказа
    setValue('itemDateField2', currentItemData.item);
    setValue('itemDateField3', currentItemData.time);
    setValue('itemDateField4', currentItemData.price);
    setValue('itemDateField5', currentItemData.date);
    setValue('itemDateField6', currentItemData.item);

    applyOrderButtonState(currentItemData.orderStatus);

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

  function resetSheetInteractions() {
    // на всякий случай возвращаем sheet в нормальное состояние
    isDragging = false;
    startY = 0;
    currentY = 0;
    if (sheet) {
      sheet.style.transition = "";
      sheet.style.transform = "";
      // по умолчанию разрешаем вертикальные жесты
      sheet.style.touchAction = "pan-y";
    }
  }

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
    // делаем идемпотентно: можно вызывать сколько угодно раз
    isRateOpen = false;
    if (rateOverlay) rateOverlay.classList.remove("active");

    // снимаем любые блокировки свайпа
    resetSheetInteractions();
  }

  // делаем доступным для других скриптов (например, ajax_menu.js)
  window.openRate = openRate;
  window.closeRate = closeRate;
  window.resetSheetInteractions = resetSheetInteractions;
  window.setRating = setRating;
  window.applyOrderButtonState = applyOrderButtonState;

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

  function openPayment() {
    if (!paymentOverlay) return;
    paymentOverlay.classList.add("active");
    lockBody(true);
  }

  function closePayment() {
    if (!paymentOverlay) return;
    paymentOverlay.classList.remove("active");
    lockBody(false);
  }

  if (openPaymentBtn) {
    openPaymentBtn.addEventListener("click", e => {
      e.preventDefault();
      openPayment();
    });
  }

  if (paymentClose) {
    paymentClose.addEventListener("click", closePayment);
  }

  if (paymentOverlay) {
    paymentOverlay.addEventListener("click", e => {
      if (e.target === paymentOverlay) {
        closePayment();
      }
    });
  }
});