import json
from datetime import datetime, date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from admin_main.models import BuyOrder
from chef_main.models import Ingredient
from menu.models import Meal, DayOrder, MenuItem


# Create your views here.


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
    a, b = meals_view()
    context = {
        'orders': BuyOrder.objects.all(),
        'meals_b': a,
        'meals_l': b,
        'today': '2026-02-05',
        'ingredients': Ingredient.objects.all(),

    }
    for i in a:
        print(i.count_by_days['2026-02-05'])

    print(meals_view())
    return render(request, 'chef_main/chef_main.html', context)


def meals_view():
    ans1, ans2 = [], []
    menu_t = DayOrder.objects.get(day=1)
    for i in menu_t.order:
        m = MenuItem.objects.get(id=i)
        if m.category in 'breakfastЗавтрак':
            for j in m.meals.all():
                ans1.append(j)
        else:
            for j in m.meals.all():
                ans2.append(j)
    return ans1, ans2



@require_POST
def update_issued_count(request):
    """Обновление количества выданных порций"""
    try:
        data = json.loads(request.body)
        print(data)
        g = Meal.objects.get(id=data['meal_id'])
        g.count_by_days['2026-02-05']['g'] += int(data['amount'])
        g.save()
        print(g.count_by_days)
        return JsonResponse({
            'success': True,
            'message': 'Данные получены успешно',
            'received_data': data,
            'test_response': {
                'issued_count': 15,
                'available_count': 25
            }
        })
    except:
        print(23)