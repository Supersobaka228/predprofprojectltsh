import json
from datetime import datetime, date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from admin_main.models import BuyOrder
from admin_main.views import sum_orders_count, sum_comes
from chef_main.models import Ingredient
from menu.models import Meal, DayOrder, MenuItem, MealIngredient


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
            BuyOrder.objects.create(items=ingredient, user_id=request.user, summ=int(total_cents))
        return redirect('chef_main')
    a, b = meals_view()
    user_buyorders = BuyOrder.objects.filter(user_id=request.user).order_by('-date')
    all_buyorders = BuyOrder.objects.order_by('-date')[:100]
    menu = MenuItem.objects.all()
    today_str = date.today().isoformat()
    context = {
        'orders': BuyOrder.objects.all(),
        'user_buyorders': user_buyorders,
        'all_buyorders': all_buyorders,
        'meals_b': a,
        'meals_l': b,
        'today': today_str,
        'ingredients': Ingredient.objects.all(),
        'buyorders_count': len(BuyOrder.objects.all()),
        'menu': len(menu),
        'summ': sum_orders_count(),
        'sum_comes': sum_comes(),
        'remains': get_remains_dict()
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


def meals_view():
    ans1, ans2 = [], []
    today_weekday = date.today().isoweekday()
    day_key = today_weekday if 1 <= today_weekday <= 5 else 5 # ВОЗМОЖНЫЙ НЕДОЧЁТ, тут можно менять для тестов днеи недели. Сейчас если сб-вс то отображает пятницу
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
        date_str = data.get('date') or date.today().strftime('%Y-%m-%d')

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
            if day_data.get('g', 0) + amount <= get_remains_dict()[meal.id]:
                day_data['g'] = day_data.get('g', 0) + amount
                meals_give(amount, meal_id)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Недостаточно доступных порций'
                })

        elif action == 'return':
            # Возврат порций

            meals_give(amount, meal_id)
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


def meals_give(amount, meal_id):
    f = Meal.objects.get(id=meal_id)

    for i in f.ingredients.all():
        d = MealIngredient.objects.get(meal=f.id, ingredient=i.id)
        i.remains -= amount * d.mass
        i.save()
        print(i.remains)

