document.addEventListener('DOMContentLoaded', () => {
    const openOverlayBtn = document.getElementById('openOverlay');
    const closeOverlayBtn = document.getElementById('closeOverlay');
    const sheetRatingOverlay = document.getElementById('sheetRatingOverlay');
    // Скрываем оверлей при загрузке, так как в CSS он по умолчанию виден
    if (sheetRatingOverlay) {
        sheetRatingOverlay.style.display = 'none';
    }


    function filterReviews(selectedId) {
    const allReviews = document.querySelectorAll('.sheet-review');
    console.log("Ищем отзывы для ID блюда:", selectedId);
    console.log("Всего найдено блоков отзывов на странице:", allReviews.length);

    let foundCount = 0;

    allReviews.forEach(review => {
        const reviewItemId = review.getAttribute('data-item-id');

        // ВАЖНО: используем == (два равно), чтобы не зависеть от типа (строка или число)
        if (reviewItemId == selectedId) {
            review.style.display = "block";
            foundCount++;
        } else {
            review.style.display = "none";
        }
    });

    console.log("В итоге показано отзывов:", foundCount);
}



    // Открытие оверлея
    if (openOverlayBtn && sheetRatingOverlay) {
        openOverlayBtn.addEventListener('click', (e) => {
            e.preventDefault(); // На случай если это внутри формы или ссылки
            // Используем flex для возможности центрирования содержимого в будущем
            sheetRatingOverlay.style.display = 'flex';
            sheetRatingOverlay.style.justifyContent = 'center';
            sheetRatingOverlay.style.alignItems = 'center';
            console.log(113);

            const currentItemData = button.getAttribute('data-item');
            console.log("Значение data-item:", currentItemData);


            filterReviews(currentItemData);


            overlay.classList.add("active");
            const lockBody = (val) => console.log("Прокрутка заблокирована:", val);


            lockBody(true);
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
