from django.shortcuts import render

from admin_main.models import BuyOrder
from chef_main.models import Ingredient


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
    context = {
        'orders': BuyOrder.objects.all(),
    }


    return render(request, 'chef_main/chef_main.html', context)