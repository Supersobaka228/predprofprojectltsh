document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('customersTraffic').getContext('2d');

  const getScale = () => {
    const baseWidth = 1920;
    const scale = window.innerWidth / baseWidth;
    return Math.min(1.4, Math.max(0.8, scale));
  };

  const applyResponsiveOptions = (chart) => {
    const scale = getScale();
    const fontSize = Math.round(12 * scale);

    chart.data.datasets[0].pointRadius = Math.round(4 * scale);
    chart.data.datasets[0].borderWidth = Math.round(2 * scale);
    chart.data.datasets[0].pointBorderWidth = Math.round(2 * scale);

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

  const data = {
    labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'],
    datasets: [{
      label: 'Продажи',
      data: date2,
      borderColor: '#000000',  // цвет линии
      backgroundColor: '#0091ff6f',  // цвет заливки под линией
      fill: true,  // заливка под линией
      tension: 0,  // сглаживание линии
      pointRadius: 4,  // размер точек
      borderWidth: 2,
      pointBorderWidth: 2,
      pointBackgroundColor: '#ffffff',

    }]
  };

  const config = {
    type: 'line',  // тип графика — линия
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 100,
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(0, 0, 0, 0.36)', borderDash: [5,5] },
          border: { display: false },
          ticks: {
            callback: function(value) {
              return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
            },
            color: '#1f2a255f',
            font: {
              weight: 600,
              family: '"M PLUS Rounded 1c", sans-serif',
            },
            autoSkip: true,
            maxTicksLimit: 6
          }
        },
        x: {
          grid: { drawBorder: false,
            display: false },
          border: { display: false },
          ticks: {
            color: '#1f2a255f',
            font: {
              weight: 600,
              family: '"M PLUS Rounded 1c", sans-serif',
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

  const myChart = new Chart(ctx, config);
  applyResponsiveOptions(myChart);
  myChart.update('none');

  window.addEventListener('resize', () => {
    applyResponsiveOptions(myChart);
    myChart.update('none');
  });
});
