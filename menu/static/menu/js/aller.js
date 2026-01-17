document.addEventListener('DOMContentLoaded', () => {

    const settings = document.querySelector('.settings_main');
    const allergens = document.querySelector('.allergens_main');

    const addAllerBtn = document.querySelector('.user_add_aller');
    const backBtn = document.querySelector('.back_to_settings');

    function resetScreens() {
        [settings, allergens].forEach(screen => {
            screen.classList.remove('is-active', 'is-exit-left');
            screen.style.transform = 'translateX(100%)';
        });
    }

    function showSettings() {
        resetScreens();

        settings.classList.add('is-active');
        settings.style.transform = 'translateX(0)';
    }

    function showAllergens() {
        resetScreens();

        settings.classList.add('is-exit-left');
        settings.style.transform = 'translateX(-100%)';

        allergens.classList.add('is-active');
        allergens.style.transform = 'translateX(0)';
    }

    addAllerBtn.addEventListener('click', showAllergens);
    backBtn.addEventListener('click', showSettings);

});
