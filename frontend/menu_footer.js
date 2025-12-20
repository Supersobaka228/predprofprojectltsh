document.addEventListener('DOMContentLoaded', () => {
  const footer = document.querySelector('.menu_footer');
const locator = document.querySelector('.footer_locator');
const highlight = document.querySelector('.footer_highlight');
const buttons = locator.querySelectorAll('.footer_container');

function moveHighlight(button) {
  const buttonRect = button.getBoundingClientRect();
  const locatorRect = locator.getBoundingClientRect();

  // Позиция относительно контейнера footer_locator
  const offsetX = -11; // смещение вправо в пикселях (подкорректируй под свои нужды)
const left = buttonRect.left - locatorRect.left + offsetX;
  const width = buttonRect.width * 1.5;

  highlight.style.left = `${left}px`;
  highlight.style.width = `${width}px`;

  // Чтобы по вертикали было точно по нижнему краю кнопок,
  // выставим высоту и bottom:
  // Так как highlight абсолютный в footer,
  // можем подвинуть highlight на высоту футера минус высоту полоски

  // При необходимости, можно сместить highlight по вертикали:
  // highlight.style.bottom = '8px'; // например, если нужно чуть выше
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
