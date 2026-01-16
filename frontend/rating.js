document.addEventListener('DOMContentLoaded', () => {
    const openOverlayBtn = document.getElementById('openOverlay');
    const closeOverlayBtn = document.getElementById('closeOverlay');
    const sheetRatingOverlay = document.getElementById('sheetRatingOverlay');

    // Скрываем оверлей при загрузке, так как в CSS он по умолчанию виден
    if (sheetRatingOverlay) {
        sheetRatingOverlay.style.display = 'none';
    }

    // Открытие оверлея
    if (openOverlayBtn && sheetRatingOverlay) {
        openOverlayBtn.addEventListener('click', (e) => {
            e.preventDefault(); // На случай если это внутри формы или ссылки
            // Используем flex для возможности центрирования содержимого в будущем
            sheetRatingOverlay.style.display = 'flex';
            sheetRatingOverlay.style.justifyContent = 'center';
            sheetRatingOverlay.style.alignItems = 'center';
        });
    }

    // Закрытие оверлея
    if (closeOverlayBtn && sheetRatingOverlay) {
        closeOverlayBtn.addEventListener('click', (e) => {
            e.preventDefault();
            sheetRatingOverlay.style.display = 'none';
        });
    }
});
