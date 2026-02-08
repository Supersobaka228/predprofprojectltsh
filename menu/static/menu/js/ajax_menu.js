// Универсальная AJAX-обвязка для menu.html
// Исключение: аллергенов (aller.js / update_allergens) пока не трогаем.

document.addEventListener('DOMContentLoaded', () => {
  const balanceEls = [
    document.querySelector('.balance_money'),
    document.querySelector('.st_balance'),
    document.querySelector('#paymentOverlay .payment-label')
  ].filter(Boolean);

  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }

  function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
  }

  function isOverlayActive(el) {
    return !!el && el.classList.contains('active');
  }

  function closeOverlayById(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('active');
  }

  function showToast(text) {
    const t = document.createElement('div');
    t.textContent = text;
    t.style.position = 'fixed';
    t.style.left = '50%';
    t.style.top = '12px';
    t.style.transform = 'translateX(-50%)';
    t.style.padding = '10px 14px';
    t.style.borderRadius = '12px';
    t.style.background = 'rgba(0,0,0,0.75)';
    t.style.color = '#fff';
    t.style.zIndex = '99999';
    t.style.fontSize = '14px';
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2200);
  }

  function updateBalance(balanceDisplay) {
    if (!balanceDisplay) return;
    // Обновляем в видимых местах
    const wallet = document.querySelector('.balance_money');
    if (wallet) wallet.textContent = balanceDisplay + '₽';

    const settings = document.querySelector('.st_balance');
    if (settings) settings.textContent = balanceDisplay + '₽';

    const paymentLabel = document.querySelector('#paymentOverlay .payment-label');
    if (paymentLabel) {
      // там строка вида "Текущий баланс: ...₽"
      paymentLabel.textContent = 'Текущий баланс: ' + balanceDisplay + '₽';
    }
  }

  function ensureHistoryDay(dateKey) {
    const container = document.querySelector('.history_container');
    if (!container) return null;

    const key = (dateKey || '').trim();
    if (!key) return null;

    // Пытаемся найти существующий день
    const days = Array.from(container.querySelectorAll('.history_day'));
    for (const d of days) {
      const title = d.querySelector('.history_day_title');
      if (title && title.textContent.trim() === key) {
        return d;
      }
    }

    // Если истории было "пусто" — убираем сообщение
    const noHistory = container.querySelector('.no-history');
    if (noHistory) noHistory.remove();

    // Создаём новый блок дня
    const dayDiv = document.createElement('div');
    dayDiv.className = 'history_day';
    dayDiv.innerHTML = `
      <p class="history_day_title"></p>
      <section class="history_section"></section>
    `;
    dayDiv.querySelector('.history_day_title').textContent = key;
    container.prepend(dayDiv);
    return dayDiv;
  }

  function appendHistoryRow(dateKey, order) {
    if (!order) return;
    const dayBlock = ensureHistoryDay(dateKey);
    if (!dayBlock) return;
    const section = dayBlock.querySelector('.history_section');
    if (!section) return;

    // Если внутри секции есть "Нет заказов" — убираем
    const noOrders = section.querySelector('.no-orders');
    if (noOrders) noOrders.remove();

    const row = document.createElement('div');
    row.className = 'history_row';
    row.innerHTML = `
      <p class="history_time"></p>
      <p class="history_item"></p>
      <p class="history_price"></p>
    `;
    row.querySelector('.history_time').textContent = order.time || '--:--';
    row.querySelector('.history_item').textContent = order.name || 'Без категории';
    row.querySelector('.history_price').textContent = String(order.price ?? 0) + '₽';

    // Добавляем в начало дня
    section.prepend(row);
  }

  async function postFormAjax(form) {
    const csrfToken = getCsrfToken();
    const fd = new FormData(form);

    const resp = await fetch(form.action || window.location.href, {
      method: 'POST',
      body: fd,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrfToken,
      },
      credentials: 'same-origin'
    });

    const isJson = (resp.headers.get('content-type') || '').includes('application/json');
    const data = isJson ? await resp.json() : null;

    if (!resp.ok) {
      throw data || { success: false };
    }

    return data;
  }

  function updateOrderStatusInList(itemId, date, status) {
    if (!itemId || !date) return;
    const el = document.querySelector(`.openSheet[data-item="${itemId}"][data-date="${date}"]`);
    if (el) el.setAttribute('data-order-status', status || '');
  }

  // 1) Пополнение баланса (payment overlay)
  const topupForm = document.querySelector('#paymentOverlay form.payment-card');
  if (topupForm) {
    topupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        const data = await postFormAjax(topupForm);
        if (data?.success) {
          updateBalance(data.balance_display);
          showToast('Баланс пополнен');
          // закрываем оверлей (CSS уже умеет)
          closeOverlayById('paymentOverlay');
          topupForm.reset();
        } else {
          showToast('Не удалось пополнить');
        }
      } catch (err) {
        showToast('Ошибка пополнения');
      }
    });
  }

  const subscribeButton = document.querySelector('.payment-subscribe');
  if (subscribeButton) {
    subscribeButton.addEventListener('click', async () => {
      const url = subscribeButton.dataset.subscribeUrl;
      if (!url) return;
      subscribeButton.disabled = true;
      try {
        const csrfToken = getCsrfToken();
        const resp = await fetch(url, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
          },
          credentials: 'same-origin',
        });
        const data = await resp.json();
        if (!resp.ok) {
          throw data;
        }
        if (data?.success) {
          if (data.balance_display) updateBalance(data.balance_display);
          showToast('Абонемент активирован');
          closeOverlayById('paymentOverlay');
        }
      } catch (err) {
        const message = err?.error || 'Не удалось оформить абонемент';
        showToast(message);
      } finally {
        subscribeButton.disabled = false;
      }
    });
  }

  // 2) Заказ блюда из sheet (order-form)
  const orderForm = document.getElementById('order-form');
  if (orderForm) {
    orderForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const orderBtn = orderForm.querySelector('.sheet_order_btn');
      const currentStatus = orderBtn?.dataset?.orderStatus || '';
      const itemId = orderForm.querySelector('[name="item"]')?.value || '';
      const day = orderForm.querySelector('[name="day"]')?.value || '';

      if (currentStatus === 'ordered') {
        const confirmUrl = orderForm.getAttribute('data-confirm-url') || '';
        if (!confirmUrl) {
          showToast('Не удалось подтвердить');
          return;
        }
        try {
          const csrfToken = getCsrfToken();
          const fd = new FormData();
          fd.append('item_id', itemId);
          fd.append('day', day);

          const resp = await fetch(confirmUrl, {
            method: 'POST',
            body: fd,
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': csrfToken,
            },
            credentials: 'same-origin'
          });

          const data = await resp.json();
          if (!resp.ok || !data?.success) {
            showToast(data?.error || 'Не удалось подтвердить');
            return;
          }

          updateOrderStatusInList(itemId, day, data.status || 'confirmed');
          if (typeof window.applyOrderButtonState === 'function') {
            window.applyOrderButtonState(data.status || 'confirmed');
          }
          showToast('Получение подтверждено');
        } catch (err) {
          showToast('Ошибка подтверждения');
        }
        return;
      }

      try {
        const data = await postFormAjax(orderForm);
        if (data?.success && data.action === 'order') {
          if (data.balance_display) updateBalance(data.balance_display);
          if (data.order && data.date_key) {
            appendHistoryRow(data.date_key, data.order);
          }
          updateOrderStatusInList(itemId, day, data.order_status || 'ordered');
          if (typeof window.applyOrderButtonState === 'function') {
            window.applyOrderButtonState(data.order_status || 'ordered');
          }
          showToast('Заказ оформлен');
          closeOverlayById('overlay');
        } else {
          showToast('Не удалось заказать');
        }
      } catch (err) {
        const errorCode = err?.error_code || '';
        if (errorCode === 'ALREADY_ORDERED') {
          updateOrderStatusInList(itemId, day, 'ordered');
          if (typeof window.applyOrderButtonState === 'function') {
            window.applyOrderButtonState('ordered');
          }
          showToast('Заказ уже оформлен');
          return;
        }
        if (errorCode === 'ALREADY_CONFIRMED') {
          updateOrderStatusInList(itemId, day, 'confirmed');
          if (typeof window.applyOrderButtonState === 'function') {
            window.applyOrderButtonState('confirmed');
          }
          showToast('Заказ уже получен');
          return;
        }
        const msg = (err && (err.error || err.message)) ? (err.error || err.message) : 'Ошибка заказа';
        showToast(msg);
      }
    });
  }

  // 3) Отзыв (review-form)
  const reviewForm = document.getElementById('review-form');
  if (reviewForm) {
    reviewForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Сначала закрываем оверлей отзыва тем же кодом, что и «Отмена»,
      // чтобы гарантированно разблокировать sheet до любых async-операций.
      if (typeof window.closeRate === 'function') {
        window.closeRate();
      } else {
        closeOverlayById('rateOverlay');
      }
      if (typeof window.resetSheetInteractions === 'function') {
        window.resetSheetInteractions();
      }

      try {
        const data = await postFormAjax(reviewForm);
        if (data?.success && data.action === 'review') {
          // Добавим отзыв в DOM, чтобы он появился без перезагрузки
          const r = data.review;
          const container = document.getElementById('reviews-container');
          if (container && r) {
            const userId = String(r.user_id ?? '');
            const itemId = String(r.item_id ?? '');
            const selector = userId ? `.sheet-review[data-review-item-id="${itemId}"][data-review-user-id="${userId}"]` : '';
            const existingReview = selector ? container.querySelector(selector) : null;
            const div = existingReview || document.createElement('div');
            div.className = 'sheet-review';
            div.setAttribute('data-review-item-id', itemId);
            if (userId) div.setAttribute('data-review-user-id', userId);
            div.innerHTML = `
              <div class="sheet-review-top">
                <div class="sheet-review-date">${r.day || ''}</div>
                <div class="sheet-review-user"></div>
                <div class="sheet-review-stars"></div>
              </div>
              <div class="sheet-review-text"></div>
            `;
            div.querySelector('.sheet-review-text').textContent = r.text || '';
            div.querySelector('.sheet-review-user').textContent = r.reviewer_name || 'Ученик';
            const starsEl = div.querySelector('.sheet-review-stars');
            const n = Number(r.stars_count || 0);
            for (let i = 0; i < 5; i++) {
              const img = document.createElement('img');
              img.src = '../../static/menu/icon/Star 1.svg';
              img.alt = '';
              img.className = 'sheet-rating-star' + (i >= n ? ' sheet-rating-star--empty' : '');
              starsEl.appendChild(img);
            }
            if (!existingReview) {
              container.appendChild(div);
            }
          }

          const ratingAvg = Number(data.rating_avg ?? 0);
          const ratingCount = Number(data.rating_count ?? 0);
          const itemId = String(r?.item_id ?? '');
          const itemEl = itemId ? document.querySelector(`.openSheet[data-item="${itemId}"]`) : null;
          if (itemEl) {
            itemEl.setAttribute('data-rating-avg', String(ratingAvg));
            itemEl.setAttribute('data-rating-count', String(ratingCount));
          }
          if (typeof window.setRating === 'function') {
            window.setRating(ratingAvg);
          }

          showToast('Отзыв отправлен');

          // На всякий случай ещё раз сбрасываем блокировки, если какие-то события залипли
          if (typeof window.resetSheetInteractions === 'function') {
            window.resetSheetInteractions();
          }

          reviewForm.reset();
        } else {
          showToast('Не удалось отправить отзыв');
        }
      } catch (err) {
        showToast('Ошибка отправки отзыва');
      }
    });
  }

  // 4) Аллергены (allergens-form) — отдельный AJAX, чтобы не было полного перехода/ошибки ссылки
  const allergensForm = document.getElementById('allergens-form');
  if (allergensForm) {
    allergensForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        const data = await postFormAjax(allergensForm);
        if (data?.success) {
          // Обновляем список в настройках
          const ul = document.getElementById('user-allergens-list');
          if (ul) {
            ul.innerHTML = '';
            const names = data.selected_names || [];
            if (names.length === 0) {
              const li = document.createElement('li');
              li.className = 'st_allergens_empty';
              li.textContent = 'Не выбраны';
              ul.appendChild(li);
            } else {
              names.forEach(n => {
                const li = document.createElement('li');
                li.textContent = n;
                ul.appendChild(li);
              });
            }
          }

          // Плавно возвращаемся на settings экран (логика как в aller.js)
          const settings = document.querySelector('.settings_main');
          const allergens = document.querySelector('.allergens_main');
          if (settings && allergens) {
            // resetScreens + showSettings
            [settings, allergens].forEach(screen => {
              screen.classList.remove('is-active', 'is-exit-left');
              screen.style.transform = 'translateX(100%)';
            });
            settings.classList.add('is-active');
            settings.style.transform = 'translateX(0)';
          }

          showToast('Аллергены сохранены');
        } else {
          showToast('Не удалось сохранить аллергены');
        }
      } catch (err) {
        showToast('Ошибка сохранения аллергенов');
      }
    });
  }
});
