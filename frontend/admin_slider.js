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
});
