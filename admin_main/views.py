import json
from datetime import datetime, timedelta
from tkinter import Menu

import dateparser
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from admin_main.models import BuyOrder, Notification
from chef_main.models import Ingredient
from menu.models import MenuItem, Order, Review, Meal, DayOrder, Allergen, MealIngredient


@csrf_exempt
@login_required
def admin(request):
    menu = MenuItem.objects.all()
    user = request.user
    context = {
        'current_user': user,
        'notifications': Notification.objects.all(),
        'buyorders': BuyOrder.objects.all(),
        'buyorders_count': len(BuyOrder.objects.all()),
        'data': orders_by_date(),
        'menu': len(menu),
        'summ': sum_orders_count(),
        'sum_comes': sum_comes(),
        'comes_by_date': comes_by_date(),
        'orders_by_day': orders_by_day(),
        'comes_by_day': comes_by_day(),
        'reviews_by_day': reviews_by_day(),
        'all_reviews': list(Review.objects.all()),
        'ingredients': Ingredient.objects.all(),
        'allergens': Allergen.objects.all(),



    }
    if request.method == 'POST':
        post = request.POST
        errors = []

        category = post.get('category')
        day_value = post.get('day')
        time_start = post.get('time_start')
        time_end = post.get('time_end')
        price_raw = post.get('price')

        dish_names = post.getlist('dish_name[]')
        dish_weights = post.getlist('dish_weight[]')
        dish_kcals = post.getlist('dish_kcal[]')

        if not category:
            errors.append('Не выбран тип приёма пищи.')
        if not time_start or not time_end:
            errors.append('Не задано время выдачи.')
        if not price_raw:
            errors.append('Не задана цена.')
        if not dish_names:
            errors.append('Не добавлено ни одного блюда.')

        if errors:
            context['errors'] = errors
            return render(request, 'admin_main/admin_main.html', context)

        meals = []
        total_calories = 0

        for i, name in enumerate(dish_names):
            name = name.strip()
            if not name:
                errors.append('Название блюда не может быть пустым.')
                continue

            try:
                weight = int(dish_weights[i]) if i < len(dish_weights) and dish_weights[i] else 0
            except ValueError:
                weight = 0

            try:
                calories = int(dish_kcals[i]) if i < len(dish_kcals) and dish_kcals[i] else 0
            except ValueError:
                calories = 0

            total_calories += calories

            dish_allergens = post.getlist(f'allergens_{i}[]')
            dish_ingredients = post.getlist(f'ingredients_{i}[]')
            dish_ingredients_grams = post.getlist(f'ingredients_grams_{i}[]')

            if not dish_allergens:
                errors.append(f'Не выбраны аллергены для блюда №{i + 1}.')
            if not dish_ingredients:
                errors.append(f'Не выбраны ингредиенты для блюда №{i + 1}.')

            meal = Meal.objects.create(
                name=name,
                weight=weight,
                calories=calories,
                description='',
            )

            if dish_allergens:
                allergens = Allergen.objects.filter(code__in=dish_allergens)
                meal.allergens.set(allergens)

            for j, ingredient_code in enumerate(dish_ingredients):
                ingredient = Ingredient.objects.filter(code=ingredient_code).first()
                if not ingredient:
                    continue
                grams = 0
                if j < len(dish_ingredients_grams):
                    try:
                        grams = int(dish_ingredients_grams[j])
                    except ValueError:
                        grams = 0
                if grams <= 0:
                    grams = 1
                MealIngredient.objects.create(meal=meal, ingredient=ingredient, mass=grams)

            meal.save()
            meals.append(meal)

        if errors:
            context['errors'] = errors
            return render(request, 'admin_main/admin_main.html', context)

        try:
            price = int(price_raw)
        except ValueError:
            price = 0

        menuitem = MenuItem.objects.create(
            category=category,
            time=f'{time_start} - {time_end}',
            price=price,
            calories=total_calories,
            proteins=0,
            fats=0,
            carbs=0,
            icon='',
        )
        menuitem.meals.set(meals)
        menuitem.save()

        try:
            day_number = int(day_value)
        except (TypeError, ValueError):
            day_number = None

        if day_number:
            day_order, _ = DayOrder.objects.get_or_create(day=day_number, defaults={'order': []})
            day_order.order.append(menuitem.id)
            day_order.save(update_fields=['order'])

        return render(request, 'admin_main/admin_main.html', context)
    return render(request, 'admin_main/admin_main.html', context)


@require_POST
def update_order_status(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('id')
        new_status = data.get('status') # 'allowed' или 'rejected'

        # Находим заказ в базе и обновляем его
        order = BuyOrder.objects.get(id=order_id)
        order.status = new_status
        order.save()

        return JsonResponse({'status': 'ok'})
    except BuyOrder.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Заказ не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def sum_orders_count():
    summ = 0
    for order in Order.objects.all():
        summ += order.price
    return summ

def sum_comes():
    summ = set()
    for order in Order.objects.all():
        summ.add(order.price)
    return len(summ)

def orders_by_date():
    dates = [0] * 5
    for order in Order.objects.all():
        date_obj_1 = datetime.strptime(order.day, "%Y-%m-%d").date()  # .date() убирает время
        dates[date_obj_1.weekday()] += order.price

    return dates


def comes_by_date():
    dates = [set(), set(), set(), set(), set()]
    for order in Order.objects.all():
        date_obj_1 = datetime.strptime(order.day, "%Y-%m-%d").date().weekday()
        dates[date_obj_1].add(order.user)
    return list(map(lambda x: len(x), dates))


def orders_by_day():
    dates = {}
    for order in Order.objects.all():
        date_obj_1 = datetime.strptime(order.day, "%Y-%m-%d").date()
        if date_obj_1 not in dates:
            dates[date_obj_1] = order.price
        else:
            dates[date_obj_1] += order.price
    if not dates:
        return {}
    min_date = min(dates)
    max_date = max(dates)
    result = {}
    ans = {}
    current_date = min_date - timedelta(days=(min_date.weekday()))
    while current_date <= max_date + timedelta(days=(5 - max_date.isoweekday())):
        if current_date.weekday() < 5:
            date_str = current_date.strftime("%Y-%m-%d")
            result[date_str] = dates.get(current_date, 0)
        current_date += timedelta(days=1)
    for i in range(0, len(result), 5):
        dates = result

        d = list(dates.keys())
        ans[f'{d[i]} {d[i + 4]}'] = [dates[j] for j in list(dates.keys())[i:i + 5]]

    return ans


def comes_by_day():
    dates = {}
    # 1. Собираем множества уникальных пользователей для каждой даты
    for order in Order.objects.all():
        date_obj_1 = datetime.strptime(order.day, "%Y-%m-%d").date()
        if date_obj_1 not in dates:
            dates[date_obj_1] = {order.user}  # Используем set для уникальности
        else:
            dates[date_obj_1].add(order.user)

    if not dates:
        return {}

    min_date = min(dates)
    max_date = max(dates)
    result = {}
    ans = {}

    current_date = min_date - timedelta(days=(min_date.weekday()))
    while current_date <= max_date + timedelta(days=(5 - max_date.isoweekday())):
        if current_date.weekday() < 5:
            date_str = current_date.strftime("%Y-%m-%d")
            result[date_str] = len(dates.get(current_date, set()))
        current_date += timedelta(days=1)

    d_keys = list(result.keys())
    for i in range(0, len(d_keys), 5):
        week_slice = d_keys[i:i + 5]
        ans[f'{week_slice[0]} {week_slice[-1]}'] = [result[j] for j in week_slice]

    return ans


def serialize_review(review):
    """
    Простой сериализатор — расширьте под поля вашей модели.
    """
    return {
        "id": review.pk,
        "day_raw": getattr(review, "day", None),
        "user_id": getattr(review, "user_id", getattr(review, "user", None) and getattr(review.user, "id", None)),
        # Попробуем взять текст отзыва из полей 'text' или 'body', иначе str(review)
        "text": getattr(review, "text", None) or getattr(review, "body", None) or str(review)
    }

def reviews_by_day(queryset=None):
    """
    Возвращает словарь вида:
      { "YYYY-MM-DD YYYY-MM-DD": [ {review1}, {review2}, ... ], ... }
    где для каждого 5-дневного рабочего интервала возвращаются все отзывы,
    оставленные в этот интервал (включая первые и последние дни интервала).
    """
    if queryset is None:
        queryset = Review.objects.all()

    # Собираем: date_obj (datetime.date) -> set(pk)
    dates = {}
    # PK -> (review_obj, parsed_date) для дальнейшей сериализации/сортировки
    reviews_info = {}

    for review in queryset:
        parsed = dateparser.parse(str(getattr(review, "day", "")), languages=['ru'])
        if not parsed:
            continue
        date_obj = parsed.date()
        pk = review.pk

        reviews_info[pk] = (review, date_obj)
        dates.setdefault(date_obj, set()).add(pk)

    if not dates:
        return {}

    min_date = min(dates)
    max_date = max(dates)

    # Выравниваем диапазон так же, как в comes_by_day
    start_date = min_date - timedelta(days=(min_date.weekday()))
    end_date = max_date + timedelta(days=(5 - max_date.isoweekday()))

    # Собираем последовательность рабочих дат (Mon-Fri) в диапазоне
    workday_dates = []
    cur = start_date
    while cur <= end_date:
        if cur.weekday() < 5:  # 0..4 -> Пн..Пт
            workday_dates.append(cur)
        cur += timedelta(days=1)

    ans = {}
    # Группируем по блокам по 5 рабочих дней
    for i in range(0, len(workday_dates), 5):
        block = workday_dates[i:i + 5]  # список datetime.date
        if not block:
            continue

        # Объединяем PK всех отзывов в этих днях
        pk_union = set()
        for d in block:
            pk_union |= dates.get(d, set())

        # Преобразуем PK в сериализованные отзывы
        # Сортируем по дате (reviews_info[pk][1]) и затем по pk для детерминированности
        sorted_pks = sorted(pk_union, key=lambda p: (reviews_info[p][1], p))
        reviews_serialized = [serialize_review(reviews_info[pk][0]) for pk in sorted_pks]

        # Формируем ключ "YYYY-MM-DD YYYY-MM-DD"
        key = f"{block[0].strftime('%Y-%m-%d')} {block[-1].strftime('%Y-%m-%d')}"
        ans[key] = reviews_serialized

    return ans


