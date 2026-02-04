from tkinter import Menu

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


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
                    'orders_stars': ''
                })
        else:
            # Отзыв
            s = dict(request.POST.items())
            s.pop('csrfmiddlewaretoken', None)

            s['day'] = str(format_russian_date(datetime.strptime(date_str, '%Y-%m-%d').date()))
            form = ReviewForm(s)
            if form.is_valid():
                review = form.save()
                if is_ajax:
                    return JsonResponse({'success': True, 'action': 'review', 'review': {
                        'item_id': getattr(review, 'item_id', None),
                        'day': getattr(review, 'day', ''),
                        'text': getattr(review, 'text', ''),
                        'stars_count': getattr(review, 'stars_count', 0),
                    }})
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
        'current_date': current_date.strftime('%Y-%m-%d'),
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

    # Цена в форме хранится в рублях (int). Баланс — в центах.
    try:
        price_rub = int(form.cleaned_data.get('price') or 0)
    except Exception:
        price_rub = 0
    price_cents = price_rub * 100

    if price_cents <= 0:
        return None, 'INVALID_PRICE', 'Некорректная цена'

    with transaction.atomic():
        user = request.user
        current = int(getattr(user, 'balance_cents', 0) or 0)
        if current < price_cents:
            return None, 'INSUFFICIENT_FUNDS', 'Недостаточно средств'

        user.balance_cents = current - price_cents

        user.save(update_fields=['balance_cents'])
        menu_t = MenuItem.objects.filter(id=form.cleaned_data.get('item'))
        print(menu_t.values())
        created_order = form.save()

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
