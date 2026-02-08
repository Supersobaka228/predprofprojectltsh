import json
from datetime import datetime, date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from admin_main.models import BuyOrder, Notification
from admin_main.views import sum_orders_count, sum_comes
from chef_main.models import Ingredient, LOW_STOCK_THRESHOLD
from menu.models import Meal, DayOrder, MenuItem, MealIngredient
from users.utils import get_profile_display_name, get_profile_role_label


# Create your views here.


@login_required
def chef(request):
    role = getattr(request.user, 'role', None)
    if role != 'cook' and not (request.user.is_staff or request.user.is_superuser or role == 'admin_main'):
        return redirect('menu')
    if request.method == "POST":
        post = request.POST
        print(post)
        products = post.getlist('products[]')
        quantities = post.getlist('quantities[]')
        prices = post.getlist('prices[]')
        limit = min(len(products), len(quantities), len(prices))
        buyorders_created = []
        for i in range(limit):
            product_id = products[i].strip()
            if not product_id:
                continue
            try:
                quantity = Decimal(quantities[i])
                price = Decimal(prices[i])
            except (InvalidOperation, TypeError, ValueError):
                continue
            total_cents = (quantity * price * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            ingredient = Ingredient.objects.get(id=product_id)
            buyorders_created.append(BuyOrder.objects.create(items=ingredient, user_id=request.user, summ=int(total_cents)))
        if buyorders_created:
            user_label = request.user.get_full_name() or getattr(request.user, 'email', '') or str(request.user.id)
            Notification.objects.create(
                recipient_type=Notification.RECIPIENT_ADMIN,
                recipient_user=None,
                title='buyorder_created',
                body=f'Новая заявка на закупку от {user_label}.',
            )
        return redirect('chef_main')
    day_key = _get_day_key()
    week_context = _build_week_context(day_key)
    a, b = meals_view(day_key=day_key)
    user_buyorders = BuyOrder.objects.filter(user_id=request.user).order_by('-date')
    all_buyorders = BuyOrder.objects.order_by('-date')[:100]
    menu = MenuItem.objects.all()
    today_str = date.today().isoformat()
    notifications = Notification.objects.filter(
        Q(recipient_type=Notification.RECIPIENT_ALL)
        | Q(recipient_type=Notification.RECIPIENT_CHEF)
        | (Q(recipient_type=Notification.RECIPIENT_USER) & Q(recipient_user=request.user))
    ).order_by('-created_at')

    low_stock_ingredients_count = Ingredient.objects.filter(remains__lt=LOW_STOCK_THRESHOLD).count()

    context = {
        'orders': BuyOrder.objects.all(),
        'user_buyorders': user_buyorders,
        'all_buyorders': all_buyorders,
        'meals_b': a,
        'meals_l': b,
        'today': week_context['selected_date'],
        'day_key': week_context['day_key'],
        'week_start': week_context['week_start'],
        'week_end': week_context['week_end'],
        'week_label': week_context['week_label'],
        'selected_date': week_context['selected_date'],
        'selected_date_display': week_context['selected_date_display'],
        'selected_day_label': week_context['selected_day_label'],
        'day_buttons': week_context['day_buttons'],
        'ingredients': Ingredient.objects.all(),
        'buyorders_count': len(BuyOrder.objects.all()),
        'menu': len(menu),
        'summ': sum_orders_count(),
        'sum_comes': sum_comes(),
        'remains': get_remains_dict(),
        'notifications': notifications,
        'user_model': get_user_model(),
        'profile_display_name': get_profile_display_name(request.user),
        'profile_role_label': get_profile_role_label(request.user),
        'low_stock_ingredients_count': low_stock_ingredients_count,
    }

    # Normalize legacy count_by_days payloads (non-dict or malformed items).
    for meal in a + b:
        if not isinstance(meal.count_by_days, dict):
            meal.count_by_days = {}
            meal.save(update_fields=["count_by_days"])
            continue
        bad_keys = [k for k, v in meal.count_by_days.items() if not isinstance(v, dict)]
        if bad_keys:
            for key in bad_keys:
                del meal.count_by_days[key]
            meal.save(update_fields=["count_by_days"])
    get_remains_dict()

    return render(request, 'chef_main/chef_main.html', context)


def meals_view(day_key=None):
    ans1, ans2 = [], []
    if day_key is None:
        day_key = _get_day_key()
    try:
        menu_t = DayOrder.objects.get(day=day_key)
    except DayOrder.DoesNotExist:
        return ans1, ans2
    for i in menu_t.order:
        m = MenuItem.objects.get(id=i)
        if m.category in 'breakfastЗавтрак':
            for j in m.meals.all():
                ans1.append(j)
        else:
            for j in m.meals.all():
                ans2.append(j)
    return ans1, ans2







def update_issued_count(request):
    """Обновление количества выданных порций"""
    try:
        data = json.loads(request.body)
        print("Получены данные:", data)

        meal_id = data.get('meal_id')
        action = data.get('action')  # 'issue' или 'return'
        amount = int(data.get('amount', 0))
        received_day_key = data.get('day_key')
        sanitized_day_key = _sanitize_day_key(received_day_key)
        date_str = _date_str_for_day_key(sanitized_day_key)

        # Получаем блюдо
        meal = Meal.objects.get(id=meal_id)

        # Инициализируем структуру данных, если её нет
        if date_str not in meal.count_by_days:
            meal.count_by_days[date_str] = {
                'o': 0,  # заказано
                'g': 0,  # выдано (g - выданные)  # доступно
            }


        day_data = meal.count_by_days[date_str]
        if action == 'issue':
            # Выдача порций
            available_servings = get_remains_dict()[meal.id]
            if amount <= available_servings:
                day_data['g'] = day_data.get('g', 0) + amount
                meals_give(amount, meal_id)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Недостаточно доступных порций'
                })

        elif action == 'return':
            # Возврат порций

            meals_give(amount, meal_id, release=False)
            day_data['g'] = max(0, day_data.get('g', 0) - amount)

        # Сохраняем обновленные данные
        meal.save()

        # Рассчитываем доступное количество
        available = get_remains_dict()[meal.id] - amount

        print(f"Обновлено: {meal.name}, дата: {date_str}")
        print(
            f"Выдано: {day_data['g']}, Заказано: {day_data.get('ordered', 0)}, Доступно: {available}"
        )

        return JsonResponse({
            'success': True,
            'message': 'Количество обновлено успешно',
            'issued_count': day_data['g'],
            'available_count': get_remains_dict()[meal.id],
            'ordered_count': day_data.get('ordered', 0)
        })

    except Meal.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Блюдо не найдено'
         }, status=404)
    except Exception as e:
        print(f"Ошибка: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Дополнительная функция для получения данных о блюдах
def get_meal_data(request):
    """API для получения данных о блюдах на конкретную дату"""
    date_str = request.GET.get('date') or date.today().strftime('%Y-%m-%d')
    meal_type = request.GET.get('meal_type')  # 'breakfast' или 'lunch'

    meals_data = []
    if meal_type == 'breakfast':
        meals, _ = meals_view()
    else:
        _, meals = meals_view()

    for meal in meals:
        day_data = meal.count_by_days.get(date_str, {})
        meals_data.append({
            'id': meal.id,
            'name': meal.name,
            'o': day_data.get('o', 0),
            'g': day_data.get('g', 0),
            'available': get_remains_dict()[meal.id],
            'total_weight': meal.weight
        })

    return JsonResponse({
        'date': date_str,
        'meals': meals_data,
        'success': True
    })


def get_remains_dict():
    s = Meal.objects.all()
    ans = {}
    for i in s:
        r_d = []
        for j in i.ingredients.all():
            g = MealIngredient.objects.get(ingredient=j.id, meal=i.id)

            d = int(j.remains) // int(g.mass)
            r_d.append(d)
        ans[i.id] = min(r_d)

    return ans


def _notify_low_stock(ingredient, previous_remains):
    if previous_remains >= LOW_STOCK_THRESHOLD and ingredient.remains < LOW_STOCK_THRESHOLD:
        if not ingredient.low_stock_notified:
            Notification.objects.create(
                recipient_type=Notification.RECIPIENT_ALL,
                recipient_user=None,
                title='low_stock',
                body=f'Низкий остаток: {ingredient.name}',
            )
            ingredient.low_stock_notified = True


def meals_give(amount, meal_id, *, release=True):
    f = Meal.objects.get(id=meal_id)

    for i in f.ingredients.all():
        d = MealIngredient.objects.get(meal=f.id, ingredient=i.id)
        delta = amount * d.mass
        previous_remains = i.remains
        if release:
            i.remains = max(0, i.remains - delta)
            _notify_low_stock(i, previous_remains)
            update_fields = ['remains', 'low_stock_notified']
        else:
            i.remains += delta
            if i.remains >= LOW_STOCK_THRESHOLD and i.low_stock_notified:
                i.low_stock_notified = False
            update_fields = ['remains', 'low_stock_notified']
        i.save(update_fields=update_fields)
        print(i.remains)


def _get_day_key(today=None):
    if today is None:
        today = date.today()
    weekday = today.isoweekday()
    return weekday if 1 <= weekday <= 5 else 5


def _sanitize_day_key(day_key):
    try:
        value = int(day_key)
    except (TypeError, ValueError):
        value = _get_day_key()
    if value < 1:
        value = 1
    if value > 5:
        value = 5
    return value


def _date_str_for_day_key(day_key, today=None):
    if today is None:
        today = date.today()
    week_start = today - timedelta(days=today.weekday())
    target_date = week_start + timedelta(days=day_key - 1)
    return target_date.strftime('%Y-%m-%d')


def _build_week_context(day_key, today=None):
    if today is None:
        today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=4)
    selected_date = week_start + timedelta(days=day_key - 1)

    full_names = [
        'Понедельник',
        'Вторник',
        'Среда',
        'Четверг',
        'Пятница',
        'Суббота',
        'Воскресенье',
    ]
    short_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт']

    day_buttons = []
    for index in range(5):
        day_date = week_start + timedelta(days=index)
        day_buttons.append({
            'day': index + 1,
            'date': day_date.isoformat(),
            'label': short_names[index],
        })

    return {
        'day_key': day_key,
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'selected_date': selected_date.isoformat(),
        'selected_date_display': selected_date.strftime('%d.%m.%Y'),
        'selected_day_label': full_names[day_key - 1] if 1 <= day_key <= 7 else '',
        'week_label': f"{week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m')}",
        'day_buttons': day_buttons,
    }
