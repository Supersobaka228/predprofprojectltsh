from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import ReviewForm
from .models import MenuItem, DayOrder, Review
from datetime import datetime, timedelta
import locale
from datetime import datetime, timedelta

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    pass


@csrf_exempt
@login_required
def menu(request):
    if request.method == 'POST':
        print(117)
        s = dict(request.POST.items())
        s.pop('csrfmiddlewaretoken', None)
        print(s)
        s['day'] = (datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date().isoweekday())
        form = ReviewForm(s)
        print(form.errors)
        if form.is_valid():
            print(113)
            form.save()
    date_str = request.GET.get('date')
    print(date_str, 111)
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
        menu_items = [menu_items_dict[id] for id in day_order.order if id in menu_items_dict]
    else:
        menu_items = []
    

    date_display = format_russian_date(current_date)


    prev_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')

    context = {
        'menu_items': menu_items,
        'date_display': date_display,
        'current_date': current_date.strftime('%Y-%m-%d'),
        'prev_date': prev_date,
        'next_date': next_date,
        'review_items': Review.objects.all()
    }
    review = Review.objects.first()
    if review is not None:
        print(review.text, 222)

    return render(request, 'menu/menu.html', context)



def format_russian_date(date_obj):
    months = ['янв.', 'февр.', 'мар.', 'апр.', 'мая', 'июня', 'июля', 'авг.', 'сент.', 'окт.', 'нояб.', 'дек.']
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']

    day = date_obj.day
    month = months[date_obj.month - 1]
    year = date_obj.year
    weekday = days[date_obj.isoweekday() - 1]

    return f"{day} {month} {year}, {weekday}"

