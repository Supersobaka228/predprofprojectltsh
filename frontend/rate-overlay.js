document.addEventListener("DOMContentLoaded", () => {
  const rateOverlay = document.getElementById("rateOverlay");
  const openRateBtn = document.getElementById("openRate");
  const rateCancel = document.getElementById("rateCancel");

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
});