from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import ReviewForm, OrderForm
from .models import MenuItem, DayOrder, Review, Order
from datetime import datetime, timedelta
import locale
from users.models import User

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
            created_order = order(request)
            if is_ajax:
                balance_str = getattr(request.user, 'balance_rub_str', '0.00')
                balance_display = str(balance_str).replace('.', ',')
                order_payload = None
                date_key = None
                if created_order is not None:
                    order_payload = {
                        'time': getattr(created_order, 'time', ''),
                        'name': getattr(created_order, 'name', ''),
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
def order(request):
    if request.method == 'POST':
        ordered_menu = dict(request.POST.items())
        ordered_menu.pop('csrfmiddlewaretoken', None)
        ordered_menu['user'] = request.user.id
        form = OrderForm(ordered_menu)
        if form.is_valid():
            return form.save()
    return None



@login_required
def update_allergens(request):
    """Обновление аллергенов пользователя"""
    if request.method == 'POST':
        # Получаем список выбранных аллергенов
        selected_allergens = request.POST.getlist('allergens')
        from django.db.models import Q
        # Удаляем старые аллергены пользователя

        user = User.objects.get(Q(username=request.user.username))
        user.not_like = selected_allergens
        user.save()

    return JsonResponse({'success': False, 'error': 'Неправильный метод запроса'})



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
