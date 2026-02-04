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


'''@require_POST
def update_meal_delivery(request):
    data = json.loads(request.body)
    meal_id = data.get('id')
    delta = data.get('delta')

    try:
        meal = Meal.objects.get(id=meal_id)

        # Предположим, count_by_days это JSONField
        # Нам нужно изменить значение 'v' (выдано) внутри 'today'
        current_data = meal.count_by_days

        if '2026-02-05' not in current_data:
            current_data['2026-02-05'] = {'o': 0, 'g': 0}

        # Обновляем количество
        old_v = current_data['2026-02-05'].get('g', 0)
        new_v = old_v + delta

        # Защита от отрицательных выдач
        if new_v < 0: new_v = 0

        current_data['2026-02-05']['g'] = new_v

        # Сохраняем (для JSONField важно принудительно сказать о сохранении)
        meal.count_by_days = current_data
        meal.save()

        return JsonResponse({
            'status': 'ok',
            'new_given': new_v
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)'''


