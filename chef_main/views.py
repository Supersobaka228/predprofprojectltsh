import json
from datetime import datetime, date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from admin_main.models import BuyOrder
from admin_main.views import sum_orders_count, sum_comes
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
    }
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
        day_key = data.get('day') or date.today().isoformat()
        g.count_by_days.setdefault(day_key, {'g': 0, 'o': 0, 'l': 0})
        g.count_by_days[day_key]['g'] += int(data['amount'])
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