import json
from datetime import datetime, date

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from admin_main.models import BuyOrder
from chef_main.models import Ingredient
from menu.models import Meal, DayOrder, MenuItem


# Create your views here.


def chef(request):
    if request.method == "POST":
        post = request.POST
        print(post)
        for i in range(len(post.getlist('products[]'))):
            t = post.getlist('products[]')[i]
            g = Ingredient.objects.get(name=t)
            s = BuyOrder.objects.create(items=g, user_id=request.user)
            s.save()
    a, b = meals_view()
    context = {
        'orders': BuyOrder.objects.all(),
        'meals_b': a,
        'meals_l': b,
        'today': '2026-02-05',

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

 # Ваша модель


# views.py



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