document.addEventListener('DOMContentLoaded', () => {
  const footer = document.querySelector('.menu_footer');
  const locator = document.querySelector('.footer_locator');
  const highlight = document.querySelector('.footer_highlight');
  const buttons = locator.querySelectorAll('.footer_container');

  const views = document.querySelectorAll('.app_view');

  function moveHighlight(button) {
    const buttonRect = button.getBoundingClientRect();
    const footerRect = footer.getBoundingClientRect();
    const highlightRect = highlight.getBoundingClientRect();
    const buttonCenter =
      buttonRect.left - footerRect.left + buttonRect.width / 2;

    const left = buttonCenter - highlightRect.width / 2;

    highlight.style.width = `${highlightRect.width}px`;
    highlight.style.left = `${left}px`;
  }

  function openView(name) {
  views.forEach(view => {
    view.classList.toggle('app_view--active', view.dataset.view === name);
  });
}


  moveHighlight(buttons[0]);
  buttons[0].classList.add('active');
  openView(buttons[0].dataset.view);

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      moveHighlight(btn);

      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      openView(btn.dataset.view);
    });
  });

  window.addEventListener('resize', () => {
    const activeBtn = locator.querySelector('.footer_container.active') || buttons[0];
    moveHighlight(activeBtn);
  });
});
