document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('stats_customersTraffic');
  if (!canvas) {
    return;
  }

  const ctx = canvas.getContext('2d');

  const getScale = () => {
    const baseWidth = 1920;
    const scale = window.innerWidth / baseWidth;
    return Math.min(1.4, Math.max(0.8, scale));
  };

  const applyResponsiveOptions = (chart) => {
    const scale = getScale();
    const fontSize = Math.round(12 * scale);

    chart.data.datasets.forEach((dataset) => {
      dataset.pointRadius = Math.round(4 * scale);
      dataset.borderWidth = Math.round(2 * scale);
      dataset.pointBorderWidth = Math.round(2 * scale);
    });

    chart.options.scales.x.ticks.font.size = fontSize;
    chart.options.scales.y.ticks.font.size = fontSize;
    chart.options.layout = {
      padding: {
        top: Math.round(8 * scale),
        right: Math.round(10 * scale),
        bottom: Math.round(6 * scale),
        left: Math.round(6 * scale)
      }
    };
  };


  const serverData = JSON.parse(document.getElementById('my-chart-data2').textContent);
  const serverDataKeys = Object.keys(serverData);
  let CurrentDataKey = serverDataKeys[0];
  let currentIndex = 0;

  const data = {
    labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'],
    datasets: [
      {
        label: 'Посещения',
        data: serverData[CurrentDataKey],
        borderColor: '#000000',
        backgroundColor: '#0091ff6f',
        fill: true,
        tension: 0,
        pointRadius: 5,
        borderWidth: 2,
        pointBorderWidth: 1.5,
        pointBackgroundColor: '#ffffff'
      },
      {
        label: 'Средние посещения',
        data: [510, 430, 520, 390, 560],
        borderColor: '#000000',
        backgroundColor: 'transparent',
        fill: false,
        tension: 0,
        borderDash: [6, 6],
        pointRadius: 5,
        borderWidth: 2,
        pointBorderWidth: 1.5,
        pointBackgroundColor: '#00DCF0'
      }
    ]
  };


  function updateUI() {
    console.log(data.datasets[0].data, CurrentDataKey);
    myChart.update('none');
    document.getElementById('display-stats-comes').innerText = CurrentDataKey;
  }



  document.getElementById('next-btn-sc').addEventListener('click', () => {
    // Проверяем, не дошли ли мы до конца списка
    if (currentIndex < serverDataKeys.length - 1) {
        currentIndex++; // Увеличиваем индекс на 1
        CurrentDataKey = serverDataKeys[currentIndex]; // Обновляем значение ключа

        console.log("Новый ключ:", CurrentDataKey);

        data.datasets[0].data = serverData[CurrentDataKey];

        updateUI(); // Обновляем текст в HTML
    } else {
        alert("Это последний доступный день!");
    }
  });

document.getElementById('prev-btn-sc').addEventListener('click', () => {
    if (currentIndex > 0) {
        currentIndex--;
        CurrentDataKey = serverDataKeys[currentIndex];

        // Обновляем данные графика
        data.datasets[0].data = serverData[CurrentDataKey];
        // myChart.update();

        updateUI();
    }
  });

  const config = {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 100,
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(0, 0, 0, 0.36)', borderDash: [5, 5] },
          border: { display: false },
          ticks: {
            callback: function(value) {
              return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
            },
            color: '#1f2a255f',
            font: {
              weight: 600,
              family: '"M PLUS Rounded 1c", sans-serif'
            },
            autoSkip: true,
            maxTicksLimit: 6
          }
        },
        x: {
          grid: { drawBorder: false, display: false },
          border: { display: false },
          ticks: {
            color: '#1f2a255f',
            font: {
              weight: 600,
              family: '"M PLUS Rounded 1c", sans-serif'
            },
            autoSkip: true,
            maxTicksLimit: 6
          }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: { enabled: true }
      }
    }
  };


const serverData2 = JSON.parse(document.getElementById('my-chart-data3').textContent);
const serverDataKeys2 = Object.keys(serverData2);
let CurrentDataKey2 = serverDataKeys2[0];
let currentIndex2 = 0;


function filterReviewsForItem(containerId = 'reviews_list', emptyElementId = 'sheet-review-empty') {
    const reviewsContainer = document.getElementById(containerId);
    if (!reviewsContainer) {
        console.warn(`Контейнер с ID "${containerId}" не найден.`);
        return;
    }
    document.getElementById('display-stats-reviews').innerText = CurrentDataKey2;
    const emptyEl = document.getElementById(emptyElementId);
    // Выбираем все элементы с классом 'review_meta' внутри контейнера
    const reviews = Array.from(reviewsContainer.querySelectorAll('.review_meta'));

    // Получаем список элементов, которые должны быть показаны
    // Используем CurrentDataKey2 + 1 как ключ, как в вашем коде
    const NeedItems = serverData2[CurrentDataKey2];

    // --- ГЛАВНОЕ ИСПРАВЛЕНИЕ: ПРОВЕРКА НАЛИЧИЯ ДАННЫХ ---
    if (!NeedItems || NeedItems.length === 0) {
        // Если NeedItems пуст или undefined, скрываем все отзывы и показываем "пусто"
        reviews.forEach(r => {
            r.style.display = 'none';
        });
        if (emptyEl) {
            emptyEl.style.display = ''; // Показываем сообщение "пусто"
        }
        console.log("NeedItems пуст или не определен. Ничего не отображено.");
        return; // Завершаем функцию
    }

    // Создаем Set для быстрого поиска ID
    const allowedItemIds = new Set(NeedItems.map(item => String(item.id)));

    let shown = 0;
    reviews.forEach(r => {
        const reviewItemId = r.getAttribute('data-review-item-id'); // ID элемента, к которому относится отзыв

        // Проверяем, есть ли ID этого элемента в нашем Set
        const match = reviewItemId && allowedItemIds.has(String(reviewItemId));

        r.style.display = match ? '' : 'none'; // '' для показа, 'none' для скрытия

        if (match) {
            shown += 1;
        }
    });

    // Обновляем состояние элемента "пусто"
    if (emptyEl) {
        emptyEl.style.display = shown === 0 ? '' : 'none';
    }

    console.log(`Показано ${shown} отзывов.`);
}


document.getElementById('review-before-btn').addEventListener('click', () => {
    // Проверяем, не дошли ли мы до конца списка
    if (currentIndex2 < serverDataKeys2.length - 1) {
        currentIndex2++; // Увеличиваем индекс на 1
        CurrentDataKey2 = serverDataKeys2[currentIndex2]; // Обновляем значение ключа

        console.log("Новый ключ:", CurrentDataKey2);

        filterReviewsForItem();
        document.getElementById('display-stats-reviews').innerText = CurrentDataKey2;
        myChart.update();

    } else {
        alert("Это последний доступный день!");
    }
  });

document.getElementById('review-next-btn').addEventListener('click', () => {
    if (currentIndex2 > 0) {
        currentIndex2--;
        CurrentDataKey2 = serverDataKeys2[currentIndex2];

        // Обновляем данные графика
        filterReviewsForItem();
        document.getElementById('display-stats-reviews').innerText = CurrentDataKey2;
        myChart.update();

    }
  });


  const myChart = new Chart(ctx, config);

  filterReviewsForItem();
  applyResponsiveOptions(myChart);
  myChart.update('none');

  window.addEventListener('resize', () => {
    applyResponsiveOptions(myChart);
    myChart.update('none');
  });
});
