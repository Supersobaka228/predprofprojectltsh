document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("overlay");
  const sheet = document.getElementById("sheet");
  const closeBtn = document.getElementById("closeSheet");
  const openButtons = document.querySelectorAll(".openSheet");

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
    if (e.target === overlay) {
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
