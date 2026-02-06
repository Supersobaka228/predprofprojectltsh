import json
from datetime import datetime, timedelta
from tkinter import Menu

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Prefetch

from admin_main.models import BuyOrder, Notification
from chef_main.models import Ingredient
from menu.models import MenuItem, Order, Review, Meal, DayOrder, Allergen, MealIngredient


def _get_no_allergen():
    allergen, _ = Allergen.objects.get_or_create(
        code='no',
        defaults={'name': 'Без аллергенов', 'sort_order': 0},
    )
    return allergen


def _should_clear_day(request, day_number):
    bulk_id = request.POST.get('bulk_save_id')
    if not bulk_id:
        return True

    session_key = 'bulk_cleared_days'
    cleared = request.session.get(session_key, {})
    if not isinstance(cleared, dict):
        cleared = {}

    day_key = str(day_number)
    if cleared.get(day_key) == bulk_id:
        return False

    cleared[day_key] = bulk_id
    request.session[session_key] = cleared
    return True


def clear_day_menu(day_number):
    day_order = DayOrder.objects.filter(day=day_number).first()
    if not day_order:
        return

    menuitem_ids = list(day_order.order or [])
    day_order.delete()

    if not menuitem_ids:
        return

    meal_ids = list(
        Meal.objects.filter(menu_items__id__in=menuitem_ids)
        .values_list('id', flat=True)
        .distinct()
    )

    MenuItem.objects.filter(id__in=menuitem_ids).delete()

    if meal_ids:
        Meal.objects.filter(id__in=meal_ids, menu_items__isnull=True).delete()


@csrf_exempt
@login_required
def admin(request):
    menu = MenuItem.objects.all()
    user = request.user

    reviews_qs = Review.objects.select_related('item', 'user').prefetch_related('item__meals').order_by('-day')
    reviews_payload = []
    for r in reviews_qs:
        email = getattr(getattr(r, 'user', None), 'email', '') or ''
        if '@' in email:
            reviewer = email.split('@', 1)[0]
        elif email.strip():
            reviewer = email.strip()
        elif getattr(r, 'reviewer_name', ''):
            reviewer = r.reviewer_name
        else:
            reviewer = 'Ученик'

        item = getattr(r, 'item', None)
        if item:
            if item.category == 'breakfast':
                meal_type = 'Завтрак'
            elif item.category == 'lunch':
                meal_type = 'Обед'
            else:
                meal_type = item.category
            meal_names = [m.name for m in item.meals.all()]
            if meal_names:
                target = f"К: {meal_type} - {', '.join(meal_names)}"
            else:
                target = f"К: {meal_type}"
        else:
            target = 'К: -'

        day_display = r.day.strftime('%d.%m.%y %H:%M') if getattr(r, 'day', None) else ''

        reviews_payload.append({
            'id': r.id,
            'day': day_display,
            'target': target,
            'stars_count': r.stars_count,
            'text': r.text,
            'reviewer': reviewer,
        })

    context = {
        'current_user': user,
        'notifications': Notification.objects.all(),
        'buyorders': BuyOrder.objects.order_by('-date'),
        'buyorders_count': len(BuyOrder.objects.all()),
        'data': orders_by_date(),
        'menu': len(menu),
        'summ': sum_orders_count(),
        'sum_comes': sum_comes(),
        'comes_by_date': comes_by_date(),
        'orders_by_day': orders_by_day(),
        'comes_by_day': comes_by_day(),
        'avg_orders_weekday': avg_orders_weekday_recent(),
        'avg_comes_weekday': avg_comes_weekday_recent(),
        'reviews_by_day': reviews_by_day(),
        'all_reviews': reviews_payload,
        'ingredients': Ingredient.objects.all(),
        'allergens': Allergen.objects.all(),
        'menu_prefill_data': build_menu_prefill_data(),
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

        try:
            day_number = int(day_value)
        except (TypeError, ValueError):
            day_number = None

        if day_number and _should_clear_day(request, day_number):
            clear_day_menu(day_number)

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
            else:
                meal.allergens.set([_get_no_allergen()])

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
            icon='menu/icon/meal1.svg',
        )
        menuitem.meals.set(meals)
        menuitem.save()

        if day_number:
            day_order, _ = DayOrder.objects.get_or_create(day=day_number, defaults={'order': []})
            day_order.order.append(menuitem.id)
            day_order.save(update_fields=['order'])

        return redirect('admin_main')
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

def _current_workweek_bounds(today=None):
    if today is None:
        today = datetime.today().date()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=4)
    return start_date, end_date

def orders_by_date():
    start_date, end_date = _current_workweek_bounds()
    dates = [0] * 5
    orders = Order.objects.filter(
        day__gte=start_date.isoformat(),
        day__lte=end_date.isoformat(),
    )
    for order in orders:
        try:
            date_obj_1 = datetime.strptime(order.day, "%Y-%m-%d").date()
        except ValueError:
            continue
        weekday_index = date_obj_1.weekday()
        if 0 <= weekday_index < 5:
            dates[weekday_index] += order.price

    return dates


def comes_by_date():
    start_date, end_date = _current_workweek_bounds()
    dates = [set(), set(), set(), set(), set()]
    orders = Order.objects.filter(
        day__gte=start_date.isoformat(),
        day__lte=end_date.isoformat(),
    )
    for order in orders:
        try:
            weekday_index = datetime.strptime(order.day, "%Y-%m-%d").date().weekday()
        except ValueError:
            continue
        if 0 <= weekday_index < 5:
            dates[weekday_index].add(order.user)
    return [len(day_users) for day_users in dates]


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

    # date_obj (datetime.date) -> list[review]
    dates = {}
    for review in queryset:
        if not getattr(review, "day", None):
            continue
        day_local = timezone.localtime(review.day).date()
        dates.setdefault(day_local, []).append(review)

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
        block = workday_dates[i:i + 5]
        if not block:
            continue

        reviews_in_block = []
        for d in block:
            reviews_in_block.extend(dates.get(d, []))

        # Сортируем отзывы по дате убыванию
        reviews_in_block.sort(key=lambda r: r.day or timezone.now(), reverse=True)
        reviews_serialized = [serialize_review(r) for r in reviews_in_block]

        key = f"{block[0].strftime('%Y-%m-%d')} {block[-1].strftime('%Y-%m-%d')}"
        ans[key] = reviews_serialized

    return ans


@login_required
@require_POST
def admin_report_general(request):
    start_str = request.POST.get("report_start")
    end_str = request.POST.get("report_end")

    if not start_str or not end_str:
        return render(request, "admin_main/report_general.html", {
            "labels": [],
            "values_breakfast": [],
            "values_lunch": [],
            "avg_breakfast": [],
            "avg_lunch": [],
            "range_label": "",
            "error": "Не задан период отчета.",
        })

    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
    except ValueError:
        return render(request, "admin_main/report_general.html", {
            "labels": [],
            "values_breakfast": [],
            "values_lunch": [],
            "avg_breakfast": [],
            "avg_lunch": [],
            "range_label": "",
            "error": "Неверный формат даты.",
        })

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    orders = Order.objects.select_related("name").filter(
        day__gte=start_date.isoformat(),
        day__lte=end_date.isoformat(),
    )

    sums_by_day_breakfast = {}
    sums_by_day_lunch = {}
    for order in orders:
        try:
            day_key = datetime.strptime(order.day, "%Y-%m-%d").date()
        except ValueError:
            continue
        category = getattr(order.name, "category", None)
        if category == "breakfast":
            sums_by_day_breakfast[day_key] = sums_by_day_breakfast.get(day_key, 0) + (order.price or 0)
        elif category == "lunch":
            sums_by_day_lunch[day_key] = sums_by_day_lunch.get(day_key, 0) + (order.price or 0)

    avg_totals_breakfast = [0] * 7
    avg_counts_breakfast = [0] * 7
    avg_totals_lunch = [0] * 7
    avg_counts_lunch = [0] * 7

    today = datetime.today().date()
    cutoff = today - timedelta(days=365)
    avg_orders = Order.objects.select_related("name").filter(
        day__gte=cutoff.isoformat(),
        day__lte=today.isoformat(),
    )

    daily_breakfast = {}
    daily_lunch = {}
    for order in avg_orders:
        try:
            day_key = datetime.strptime(order.day, "%Y-%m-%d").date()
        except ValueError:
            continue
        category = getattr(order.name, "category", None)
        if category == "breakfast":
            daily_breakfast[day_key] = daily_breakfast.get(day_key, 0) + (order.price or 0)
        elif category == "lunch":
            daily_lunch[day_key] = daily_lunch.get(day_key, 0) + (order.price or 0)

    for day_key, total in daily_breakfast.items():
        if total <= 0:
            continue
        weekday = day_key.weekday()
        avg_totals_breakfast[weekday] += total
        avg_counts_breakfast[weekday] += 1

    for day_key, total in daily_lunch.items():
        if total <= 0:
            continue
        weekday = day_key.weekday()
        avg_totals_lunch[weekday] += total
        avg_counts_lunch[weekday] += 1

    avg_by_weekday_breakfast = [
        (avg_totals_breakfast[i] / avg_counts_breakfast[i]) if avg_counts_breakfast[i] else 0
        for i in range(7)
    ]
    avg_by_weekday_lunch = [
        (avg_totals_lunch[i] / avg_counts_lunch[i]) if avg_counts_lunch[i] else 0
        for i in range(7)
    ]

    labels = []
    values_breakfast = []
    values_lunch = []
    avg_breakfast = []
    avg_lunch = []
    cursor = start_date
    while cursor <= end_date:
        labels.append(cursor.strftime("%d.%m"))
        values_breakfast.append(sums_by_day_breakfast.get(cursor, 0))
        values_lunch.append(sums_by_day_lunch.get(cursor, 0))
        weekday = cursor.weekday()
        avg_breakfast.append(avg_by_weekday_breakfast[weekday])
        avg_lunch.append(avg_by_weekday_lunch[weekday])
        cursor += timedelta(days=1)

    range_label = f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"

    return render(request, "admin_main/report_general.html", {
        "labels": labels,
        "values_breakfast": values_breakfast,
        "values_lunch": values_lunch,
        "avg_breakfast": avg_breakfast,
        "avg_lunch": avg_lunch,
        "range_label": range_label,
        "error": "",
    })


@login_required
@require_POST
def admin_report_costs(request):
    start_str = request.POST.get("costs_start")
    end_str = request.POST.get("costs_end")

    if not start_str or not end_str:
        return render(request, "admin_main/report_costs.html", {
            "labels": [],
            "values": [],
            "avg_values": [],
            "range_label": "",
            "error": "Не задан период отчета.",
        })

    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
    except ValueError:
        return render(request, "admin_main/report_costs.html", {
            "labels": [],
            "values": [],
            "avg_values": [],
            "range_label": "",
            "error": "Неверный формат даты.",
        })

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    orders = BuyOrder.objects.filter(
        status="allowed",
        date__date__gte=start_date,
        date__date__lte=end_date,
    )

    sums_by_day = {}
    for order in orders:
        day_key = order.date.date()
        sums_by_day[day_key] = sums_by_day.get(day_key, 0) + float(order.summ_rub)

    today = datetime.today().date()
    cutoff = today - timedelta(days=365)
    avg_orders = BuyOrder.objects.filter(
        status="allowed",
        date__date__gte=cutoff,
        date__date__lte=today,
    )

    daily_totals = {}
    for order in avg_orders:
        day_key = order.date.date()
        daily_totals[day_key] = daily_totals.get(day_key, 0) + float(order.summ_rub)

    avg_totals = [0.0] * 7
    avg_counts = [0] * 7
    for day_key, total in daily_totals.items():
        if total <= 0:
            continue
        weekday = day_key.weekday()
        avg_totals[weekday] += total
        avg_counts[weekday] += 1

    avg_by_weekday = [
        (avg_totals[i] / avg_counts[i]) if avg_counts[i] else 0
        for i in range(7)
    ]

    labels = []
    values = []
    avg_values = []
    cursor = start_date
    while cursor <= end_date:
        labels.append(cursor.strftime("%d.%m"))
        values.append(sums_by_day.get(cursor, 0))
        weekday = cursor.weekday()
        avg_values.append(avg_by_weekday[weekday])
        cursor += timedelta(days=1)

    range_label = f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"

    return render(request, "admin_main/report_costs.html", {
        "labels": labels,
        "values": values,
        "avg_values": avg_values,
        "range_label": range_label,
        "error": "",
    })


def avg_orders_weekday_recent(days_back=180):
    today = datetime.today().date()
    cutoff = today - timedelta(days=days_back)

    daily_totals = {}
    orders = Order.objects.filter(day__gte=cutoff.isoformat(), day__lte=today.isoformat())
    for order in orders:
        try:
            day_key = datetime.strptime(order.day, "%Y-%m-%d").date()
        except ValueError:
            continue
        daily_totals[day_key] = daily_totals.get(day_key, 0) + (order.price or 0)

    totals = [0] * 7
    counts = [0] * 7
    for day_key, total in daily_totals.items():
        if total <= 0:
            continue
        weekday = day_key.weekday()
        totals[weekday] += total
        counts[weekday] += 1

    return [
        (totals[i] / counts[i]) if counts[i] else 0
        for i in range(5)
    ]


def avg_comes_weekday_recent(days_back=180):
    today = datetime.today().date()
    cutoff = today - timedelta(days=days_back)

    daily_users = {}
    orders = Order.objects.filter(day__gte=cutoff.isoformat(), day__lte=today.isoformat())
    for order in orders:
        try:
            day_key = datetime.strptime(order.day, "%Y-%m-%d").date()
        except ValueError:
            continue
        daily_users.setdefault(day_key, set()).add(order.user_id)

    totals = [0] * 7
    counts = [0] * 7
    for day_key, users in daily_users.items():
        value = len(users)
        if value <= 0:
            continue
        weekday = day_key.weekday()
        totals[weekday] += value
        counts[weekday] += 1

    return [
        (totals[i] / counts[i]) if counts[i] else 0
        for i in range(5)
    ]


def buyorders_by_date(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'orders': []})
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'orders': []}, status=400)

    orders = BuyOrder.objects.filter(date__date=target_date).order_by('-date')
    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'date': order.date.strftime('%d.%m.%y'),
            'user': str(order.user_id),
            'items': str(order.items),
            'summ': f"{order.summ_rub:.2f}",
            'status': order.status,
        })
    return JsonResponse({'orders': data})

def _split_menu_time(time_value):
    if not time_value:
        return '', ''
    if '-' in time_value:
        parts = time_value.split('-', 1)
        return parts[0].strip(), parts[1].strip()
    return time_value.strip(), ''


def build_menu_prefill_data():
    day_orders = DayOrder.objects.filter(day__gte=1, day__lte=5)
    day_to_ids = {day_order.day: list(day_order.order or []) for day_order in day_orders}
    menuitem_ids = set()
    for ids in day_to_ids.values():
        menuitem_ids.update(ids)

    menuitems_by_id = {}
    if menuitem_ids:
        menuitems = (
            MenuItem.objects.filter(id__in=menuitem_ids)
            .prefetch_related(
                Prefetch(
                    'meals',
                    queryset=Meal.objects.prefetch_related(
                        'allergens',
                        Prefetch('mealingredient_set', queryset=MealIngredient.objects.select_related('ingredient')),
                    ),
                )
            )
        )

        for menuitem in menuitems:
            time_start, time_end = _split_menu_time(menuitem.time)
            meals_payload = []
            for meal in menuitem.meals.all():
                ingredients_payload = []
                for mi in meal.mealingredient_set.all():
                    ingredient = mi.ingredient
                    ingredients_payload.append({
                        'code': ingredient.code,
                        'name': ingredient.name,
                        'grams': mi.mass,
                    })

                meals_payload.append({
                    'id': meal.id,
                    'name': meal.name,
                    'weight': meal.weight,
                    'calories': meal.calories,
                    'allergens': [
                        {'code': allergen.code, 'name': allergen.name}
                        for allergen in meal.allergens.all()
                    ],
                    'ingredients': ingredients_payload,
                })

            menuitems_by_id[menuitem.id] = {
                'id': menuitem.id,
                'category': menuitem.category,
                'time_start': time_start,
                'time_end': time_end,
                'price': menuitem.price,
                'meals': meals_payload,
            }

    days_payload = {}
    for day, ids in day_to_ids.items():
        day_items = []
        for menu_id in ids:
            payload = menuitems_by_id.get(menu_id)
            if payload:
                day_items.append(payload)
        days_payload[str(day)] = day_items

    return {
        'days': days_payload,
    }
