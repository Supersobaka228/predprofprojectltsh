from django.contrib.auth import _get_compatible_backends, get_user_model
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import login
from django.contrib import messages
from rest_framework.exceptions import ValidationError

from .forms import RegisterForm, LoginForm


# Create your views here.
def register(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        form = RegisterForm(request.POST)
        form.error_messages = []
        if form.is_valid():
            print(113)
            form.save()
            return render(request, 'users/login.html')
        else:
            print(form.errors)
            form.error_messages.append('Форма неверна')
            data = {'form': form}
            return render(request, 'users/register.html', data)
    form = RegisterForm()
    data = {'form': form}
    form.error_messages = []
    return render(request, 'users/register.html', data)
    print(form)




def login_f(request):
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        form.error_messages = []
        print(form.errors)
        if form.is_bound:
            user = form.get_user()

            if not form.clean():
                request.session.set_expiry(0)
                form.set_error('Неверный логин или пароль')
                print(form.error_messages)
                return render(request, 'users/login.html', {'form': form})
            login(request, user)
            # Получаем параметр next
            next_url = request.POST.get('next') or request.GET.get('next')

            if next_url:
                return redirect(next_url)
            return redirect('menu')
    else:
        form = LoginForm(request=request)

    return render(request, 'users/login.html', {'form': form, "next": request.GET.get('next', '')})

        

