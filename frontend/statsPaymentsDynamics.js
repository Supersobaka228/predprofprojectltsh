document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('stats_paymentDynamics');
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
        top: Math.round(6 * scale),
        right: Math.round(10 * scale),
        bottom: Math.round(2 * scale),
        left: Math.round(6 * scale)
      }
    };
  };

  const data = {
    labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'],
    datasets: [
      {
        label: 'Продажи',
        data: [65000, 85000, 50000, 75000, 106000],
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
        label: 'План',
        data: [90000, 70000, 110000, 90000, 63000],
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
            padding: 2,
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
