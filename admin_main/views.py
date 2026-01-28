from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@login_required
def admin(request):
    return render(request, 'admin_main/admin_main.html')