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


  // Функция блокировки прокрутки body при открытом листе
  function lockBody(lock) {
    if (lock) {
      // Сохраняем текущий скролл, чтобы при закрытии вернуть
      const scrollY = window.scrollY || document.documentElement.scrollTop;
      document.body.style.position = "fixed";
      document.body.style.top = `-${scrollY}px`;
      document.body.style.left = "0";
      document.body.style.right = "0";
      document.body.dataset.scrollY = scrollY;  // Сохраняем в data-атрибут
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

  // Открытие листа и оверлея
  function openSheet() {
    overlay.classList.add("active");
    lockBody(true);
  }

  // Закрытие
  function closeSheet() {
    overlay.classList.remove("active");
    lockBody(false);
    sheet.style.transform = "";
  }

  // Навешиваем обработчики на кнопки открытия
  openButtons.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      openSheet();
    });
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

  function openRate() {
  isRateOpen = true;
  rateOverlay.classList.add("active");

  // блокируем взаимодействие с sheet
  sheet.style.touchAction = "none";
  }

  function closeRate() {
  isRateOpen = false;
  rateOverlay.classList.remove("active");

  sheet.style.touchAction = "";
  }

  /* Открытие */
  openRateBtn.addEventListener("click", e => {
  e.preventDefault();
  openRate();
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
