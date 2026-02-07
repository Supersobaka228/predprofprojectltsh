from tkinter import Menu

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from admin_main.models import Notification
from .forms import ReviewForm, OrderForm
from .models import MenuItem, DayOrder, Review, Order, Allergen
from datetime import datetime, timedelta
import locale

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    pass


@csrf_exempt
@login_required
def menu(request):
    role = getattr(request.user, 'role', None)
    if role == 'cook':
        return redirect('chef_main')

    date_str = request.GET.get('date')

    # Если пришёл POST без ?date=..., не пытаемся парсить None
    # (например, при сохранении аллергенов со страницы настроек).
    if not date_str:
        date_str = datetime.today().date().strftime('%Y-%m-%d')

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == 'POST':
        if 'allergens' in request.POST:
            # аллергенов пока не трогаем
            update_allergens(request)
        elif 'price' in request.POST:
            # Заказ блюда
            created_order, err_code, err_msg = order(request, request.POST.get('day'))
            if is_ajax:
                if created_order is None:
                    return JsonResponse(
                        {'success': False, 'action': 'order', 'error_code': err_code, 'error': err_msg},
                        status=400,
                    )
                balance_str = getattr(request.user, 'balance_rub_str', '0.00')
                balance_display = str(balance_str).replace('.', ',')
                order_payload = None
                date_key = None
                if created_order is not None:
                    order_payload = {
                        'time': getattr(created_order, 'time', ''),
                        'name': str(getattr(created_order, 'name', '') or ''),
                        'price': getattr(created_order, 'price', 0),
                        'day': getattr(created_order, 'day', ''),
                    }
                    # day хранится как 'YYYY-MM-DD' (в вашей модели)
                    try:
                        current_date_for_key = datetime.strptime(created_order.day, '%Y-%m-%d').date()
                        date_key = format_russian_date(current_date_for_key)
                    except Exception:
                        date_key = created_order.day



                return JsonResponse({
                    'success': True,
                    'action': 'order',
                    'balance_display': balance_display,
                    'order': order_payload,
                    'date_key': date_key,
                    'orders_stars': '',
                    'order_status': getattr(created_order, 'status', 'ordered'),
                })
        else:
            # Отзыв
            s = dict(request.POST.items())
            s.pop('csrfmiddlewaretoken', None)

            form = ReviewForm(s)
            if form.is_valid():
                existing = Review.objects.filter(item_id=form.cleaned_data.get('item'), user=request.user).first()
                review = form.save(commit=False)
                if existing:
                    review = existing
                    review.text = form.cleaned_data.get('text')
                    review.stars_count = form.cleaned_data.get('stars_count')

                user_obj = request.user
                email = getattr(user_obj, 'email', '') or ''
                if '@' in email:
                    reviewer_name = email.split('@', 1)[0]
                elif email.strip():
                    reviewer_name = email.strip()
                else:
                    reviewer_name = 'Ученик'
                review.user = request.user
                review.reviewer_name = reviewer_name
                review.day = timezone.now()
                review.save()
                if is_ajax:
                    agg = Review.objects.filter(item_id=review.item_id).aggregate(
                        avg=Avg('stars_count'),
                        count=Count('id'),
                    )
                    rating_avg = round(float(agg.get('avg') or 0), 1)
                    rating_count = int(agg.get('count') or 0)
                    day_display = timezone.localtime(review.day).strftime('%d.%m.%y %H:%M')
                    menu_item = MenuItem.objects.filter(id=review.item_id).first()
                    if menu_item:
                        if rating_avg < 3.0 and not menu_item.low_rating_notified:
                            user_label = request.user.get_full_name() or getattr(request.user, 'email', '') or str(request.user.id)
                            Notification.objects.create(
                                recipient_type=Notification.RECIPIENT_ADMIN,
                                recipient_user=None,
                                title='low_rating',
                                body=f'Рейтинг "{menu_item}" опустился ниже 3.0.',
                            )
                            menu_item.low_rating_notified = True
                            menu_item.save(update_fields=['low_rating_notified'])
                        elif rating_avg >= 3.0 and menu_item.low_rating_notified:
                            menu_item.low_rating_notified = False
                            menu_item.save(update_fields=['low_rating_notified'])
                    return JsonResponse({'success': True, 'action': 'review', 'review': {
                        'item_id': getattr(review, 'item_id', None),
                        'user_id': getattr(review, 'user_id', None),
                        'day': day_display,
                        'text': getattr(review, 'text', ''),
                        'stars_count': getattr(review, 'stars_count', 0),
                        'reviewer_name': getattr(review, 'reviewer_name', ''),
                    }, 'rating_avg': rating_avg, 'rating_count': rating_count})
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'action': 'review', 'errors': form.errors}, status=400)


    if date_str:
        try:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = datetime.today().date()
    else:
        current_date = datetime.today().date()

    current_day = current_date.isoweekday()



    try:
        day_order = DayOrder.objects.get(day=current_day)

    except DayOrder.DoesNotExist:
        day_order = None


    if day_order:
        menu_items_dict = {item.id: item for item in MenuItem.objects.filter(id__in=day_order.order)}
        menu_items = [menu_items_dict[int(id)] for id in day_order.order if int(id) in menu_items_dict]
    else:
        menu_items = []

    current_date_str = current_date.strftime('%Y-%m-%d')
    user_orders_today = Order.objects.filter(user_id=request.user.id, day=current_date_str).values('name_id', 'status')
    order_status_map = {row['name_id']: row['status'] for row in user_orders_today}
    for item in menu_items:
        item.order_status = order_status_map.get(item.id, '')

    rating_rows = Review.objects.filter(item_id__in=[i.id for i in menu_items]).values('item_id').annotate(
        avg=Avg('stars_count'),
        count=Count('id'),
    )
    ratings_map = {r['item_id']: r for r in rating_rows}
    for item in menu_items:
        row = ratings_map.get(item.id)
        avg_val = round(float(row.get('avg') or 0), 1) if row else 0.0
        item.rating_avg = avg_val
        item.rating_count = int(row.get('count') or 0) if row else 0

    date_display = format_russian_date(current_date)


    prev_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        orders = Order.objects.filter(Q(user_id=request.user.id))
    except Order.DoesNotExist:
        orders = None
    orders_d = dict_orders(orders)


    context = {
        'menu_items': menu_items,
        'date_display': date_display,
        'current_date': current_date_str,
        'prev_date': prev_date,
        'next_date': next_date,
        'review_items': Review.objects.all(),
        'orders': orders_d,
        'orders_keys': orders_d.keys()
    }

    # Аллергены: список и выбор пользователя
    try:
        context['all_allergens'] = list(Allergen.objects.all())
        context['selected_allergen_codes'] = list(request.user.allergies.values_list('code', flat=True))
        context['selected_allergen_names'] = list(request.user.allergies.values_list('name', flat=True))
    except Exception:
        context['all_allergens'] = []
        context['selected_allergen_codes'] = []
        context['selected_allergen_names'] = []

    # Баланс для отображения: 2 знака после запятой, разделитель запятая
    try:
        balance_str = getattr(request.user, 'balance_rub_str', '0.00')
        context['balance_display'] = str(balance_str).replace('.', ',')
    except Exception:
        context['balance_display'] = '0,00'

    # Вычисляем display_name: сначала first_name, иначе часть email до @, иначе 'Ученик'
    try:
        user_obj = request.user
        first = getattr(user_obj, 'first_name', '') or ''
        email = getattr(user_obj, 'email', '') or ''
        if first.strip():
            display_name = first.strip()
        elif '@' in email:
            display_name = email.split('@', 1)[0]
        elif email.strip():
            display_name = email.strip()
        else:
            display_name = 'Ученик'
    except Exception:
        display_name = 'Ученик'

    context['display_name'] = display_name
    return render(request, 'menu/menu.html', context)


@login_required
def order(request, day_d):
    """Создаёт заказ и списывает деньги с баланса.

    Возвращает кортеж: (created_order | None, error_code | None, error_message | None)
    """
    if request.method != 'POST':
        return None, 'BAD_METHOD', 'Неправильный метод запроса'

    ordered_menu = dict(request.POST.items())
    print(ordered_menu)
    ordered_menu.pop('csrfmiddlewaretoken', None)
    ordered_menu['user'] = request.user.id
    form = OrderForm(ordered_menu)
    if not form.is_valid():
        return None, 'INVALID_FORM', 'Неверные данные заказа'

    with transaction.atomic():
        user = request.user
        existing_order = Order.objects.filter(
            user=user,
            name=form.cleaned_data.get('name'),
            day=form.cleaned_data.get('day'),
        ).first()
        if existing_order:
            if existing_order.status == 'confirmed':
                return None, 'ALREADY_CONFIRMED', 'Заказ уже подтвержден'
            return None, 'ALREADY_ORDERED', 'Заказ уже оформлен'

        # Цена в форме хранится в рублях (int). Баланс — в центах.
        try:
            price_rub = int(form.cleaned_data.get('price') or 0)
        except Exception:
            price_rub = 0
        price_cents = price_rub * 100

        if price_cents <= 0:
            return None, 'INVALID_PRICE', 'Некорректная цена'

        current = int(getattr(user, 'balance_cents', 0) or 0)
        if current < price_cents:
            return None, 'INSUFFICIENT_FUNDS', 'Недостаточно средств'

        user.balance_cents = current - price_cents

        user.save(update_fields=['balance_cents'])
        menu_item = form.cleaned_data.get('name')
        order_day = form.cleaned_data.get('day') or str(datetime.today().date())
        meals_qs = menu_item.meals.all() if menu_item else []
        for gh in meals_qs:
            day_key = str(order_day)
            count_by_days = gh.count_by_days
            if not isinstance(count_by_days, dict):
                count_by_days = {}
            day_entry = count_by_days.get(day_key)
            if isinstance(day_entry, int):
                day_entry = {'o': day_entry, 'g': 0}
            elif not isinstance(day_entry, dict):
                day_entry = {'o': 0, 'g': 0}
            day_entry['o'] = int(day_entry.get('o', 0)) + 1
            count_by_days[day_key] = day_entry
            gh.count_by_days = count_by_days
            gh.save(update_fields=['count_by_days'])
            print(gh.__dict__)
            # NOTE: inventory decrement moved to chef_main.meals_give (actual issuance)
            # If you want orders to reserve/decrease stock at payment time,
            # re-enable subtraction here. For now we do not touch Ingredient.remains
            # when a student creates an order to keep decrements only on issuance.

        try:
            created_order = form.save()
        except IntegrityError:
            return None, 'ALREADY_ORDERED', 'Заказ уже оформлен'

        return created_order, None, None



@login_required
def update_allergens(request):
    """Обновление аллергенов пользователя (фиксированный список).

    Ожидаем, что форма отправляет список `allergens` со значениями = Allergen.code.
    """
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method != 'POST':
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Неправильный метод запроса'}, status=405)
        return JsonResponse({'success': False, 'error': 'Неправильный метод запроса'})

    selected_codes = [c for c in request.POST.getlist('allergens') if c]
    allergens = list(Allergen.objects.filter(code__in=selected_codes))

    # Обновляем выбор для текущего пользователя
    request.user.allergies.set(allergens)

    payload = {
        'success': True,
        'selected_codes': [a.code for a in allergens],
        'selected_names': [a.name for a in allergens],
    }

    if is_ajax:
        return JsonResponse(payload)

    # fallback: для обычной отправки формы возвращаемся в меню
    return JsonResponse(payload)


@require_POST
@login_required
def confirm_order(request):
    """Подтверждает получение заказа без повторного списания."""
    item_id = request.POST.get('item_id') or request.POST.get('item')
    day = request.POST.get('day')
    if not item_id or not day:
        return JsonResponse({'success': False, 'error': 'Недостаточно данных'}, status=400)

    order_obj = Order.objects.filter(user=request.user, name_id=item_id, day=day).first()
    if not order_obj:
        return JsonResponse({'success': False, 'error': 'Заказ не найден'}, status=404)

    if order_obj.status != 'confirmed':
        order_obj.status = 'confirmed'
        order_obj.save(update_fields=['status'])

    return JsonResponse({'success': True, 'status': order_obj.status})

def orders_stars(orders):
    ans = dict()
    for i in orders.all():
        current_date = datetime.strptime(i.day, '%Y-%m-%d').date()
        r = format_russian_date(current_date)
        if r in ans.keys():
            ans[r] = (ans[r][0] + int(i.stars_count), ans[r][1] + 1)
        else:
            ans[r] = (i.stars_count, 1)
        ans[r] = ans[r][0] / ans[r][1]
    return ans



def dict_orders(orders):
    ans = dict()
    for i in orders.all():
        current_date = datetime.strptime(i.day, '%Y-%m-%d').date()
        r = format_russian_date(current_date)
        if r in ans.keys():
            ans[r].append(i)
        else:
            ans[r] = [i]
    return ans


def format_russian_date(date_obj):
    months = ['янв.', 'февр.', 'мар.', 'апр.', 'мая', 'июня', 'июля', 'авг.', 'сент.', 'окт.', 'нояб.', 'дек.']
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']

    day = date_obj.day
    month = months[date_obj.month - 1]
    year = date_obj.year
    weekday = days[date_obj.isoweekday() - 1]

    return f"{day} {month} {year}, {weekday}"
