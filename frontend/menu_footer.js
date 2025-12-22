document.addEventListener('DOMContentLoaded', () => {
  const footer = document.querySelector('.menu_footer');
const locator = document.querySelector('.footer_locator');
const highlight = document.querySelector('.footer_highlight');
const buttons = locator.querySelectorAll('.footer_container');

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



// Ставим изначально подсветку на первый элемент
moveHighlight(buttons[0]);
buttons[0].classList.add('active');

buttons.forEach(btn => {
  btn.addEventListener('click', () => {
    moveHighlight(btn);
    buttons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

window.addEventListener('resize', () => {
  const activeBtn = locator.querySelector('.footer_container.active') || buttons[0];
  moveHighlight(activeBtn);
});
});
