// Новый файл для расширенного извлечения data-атрибутов из кликнутого элемента .openSheet
// и заполнения sheet-overlay. Добавьте сюда свою логику наполнения overlay.

document.addEventListener("DOMContentLoaded", () => {
  const openButtons = document.querySelectorAll(".openSheet");

  let currentItemData = {}; // Глобальный объект для хранения данных текущего блюда

  // Функция для извлечения и логирования всех data-атрибутов из кликнутого элемента
  function extractItemData(e) {
    e.preventDefault();

    // Получаем кликнутый элемент (секцию)
    const button = e.currentTarget;

    // Извлекаем все data-атрибуты (из цикла {% for item in menu_items %} в HTML)
    currentItemData = {
      id: button.getAttribute('data-id'),
      name: button.getAttribute('data-name'),
      price: button.getAttribute('data-price'),
      time: button.getAttribute('data-time'),
      icon: button.getAttribute('data-icon'),
      max_des: button.getAttribute('data-max-des'),  // Строка с разделителем ||
      allergens: button.getAttribute('data-allergens'),  // Строка с разделителем ||
      date: button.getAttribute('data-date'),
      category: button.getAttribute('data-category')
    };

    // Логируем объект для отладки — он содержит все данные текущего блюда
    console.log('Извлечённые data-атрибуты из кликнутого элемента:', currentItemData);

    // Теперь данные в currentItemData — их можно использовать для дальнейшего наполнения UI (например, в вашем коде)
    // Пример: если нужно разделить списки (для UI)
    if (currentItemData.max_des) {
      currentItemData.max_des_list = currentItemData.max_des.split('||');  // Массив для простоты
    }
    if (currentItemData.allergens) {
      currentItemData.allergens_list = currentItemData.allergens.split('||');  // Массив
    }

    console.log('Обрабатываемые списки (для вашего использования):', {
      max_des_list: currentItemData.max_des_list,
      allergens_list: currentItemData.allergens_list
    });

    // Здесь можно вызвать вашу функцию populateSheet(currentItemData), но оставляем за вами
  }

  // Навешиваем обработчик на все кнопки .openSheet (то же, что в sheet.js, но только для данных)
  openButtons.forEach(btn => {
    btn.addEventListener("click", extractItemData);
  });

  // Экспорт для использования в других файлах JS (если нужно, например, в sheet.js)
  window.sheetData = { currentItemData };
});