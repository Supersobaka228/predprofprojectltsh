import json
from datetime import datetime, date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from admin_main.models import BuyOrder
from chef_main.models import Ingredient
from menu.models import Meal, DayOrder, MenuItem


def chef(request):
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

    # Получаем текущую дату
    today_str = date.today().strftime('%Y-%m-%d')

    a, b = meals_view()
    user_buyorders = BuyOrder.objects.filter(user_id=request.user).order_by('-date')
    all_buyorders = BuyOrder.objects.order_by('-date')[:100]

    context = {
        'orders': BuyOrder.objects.all(),
        'user_buyorders': user_buyorders,
        'all_buyorders': all_buyorders,
        'meals_b': a,
        'meals_l': b,
        'today': today_str,
        'ingredients': Ingredient.objects.all(),
    }

    # Отладочная информация
    print(f"Сегодня: {today_str}")
    for meal in a:
        print(f"Блюдо: {meal.name}")
        print(f"Данные: {meal.count_by_days}")

    return render(request, 'chef_main/chef_main.html', context)


def meals_view():
    ans1, ans2 = [], []
    try:
        menu_t = DayOrder.objects.get(day=1)
        for i in menu_t.order:
            m = MenuItem.objects.get(id=i)
            if m.category in 'breakfastЗавтрак':
                for j in m.meals.all():
                    ans1.append(j)
            else:
                for j in m.meals.all():
                    ans2.append(j)
    except DayOrder.DoesNotExist:
        print("DayOrder для дня 1 не найден")
    except Exception as e:
        print(f"Ошибка в meals_view: {e}")

    return ans1, ans2


@require_POST
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
                'ordered': 0,  # заказано
                'g': 0,  # выдано (g - выданные)
                'available': meal.weight  # доступно
            }

        day_data = meal.count_by_days[date_str]

        if action == 'issue':
            # Выдача порций
            if day_data.get('g', 0) + amount <= day_data.get('available', meal.weight):
                day_data['g'] = day_data.get('g', 0) + amount
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Недостаточно доступных порций'
                })

        elif action == 'return':
            # Возврат порций
            day_data['g'] = max(0, day_data.get('g', 0) - amount)

        # Сохраняем обновленные данные
        meal.save()

        # Рассчитываем доступное количество
        available = day_data.get('available', meal.weight) - day_data.get('g', 0)

        print(f"Обновлено: {meal.name}, дата: {date_str}")
        print(f"Выдано: {day_data['g']}, Заказано: {day_data['o']}, Доступно: {available}")

        return JsonResponse({
            'success': True,
            'message': 'Количество обновлено успешно',
            'issued_count': day_data['g'],
            'available_count': available,
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
def get_meal_data_for_date(request):
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
            'ordered': day_data.get('ordered', 0),
            'issued': day_data.get('g', 0),
            'available': day_data.get('available', meal.weight),
            'total_weight': meal.weight
        })

    return JsonResponse({
        'date': date_str,
        'meals': meals_data,
        'success': True
    })