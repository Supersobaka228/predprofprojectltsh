from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .forms import RegisterForm, LoginForm, TopUpBalanceForm
from .models import BalanceTopUp


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
            return redirect('login')
        else:
            print(form.errors)
            form.error_messages.append('Форма неверна')
            # Render the template with the bound form to display validation errors
            return render(request, 'users/register.html', {'form': form})
    form = RegisterForm()
    data = {'form': form}
    form.error_messages = []
    return render(request, 'users/register.html', data)


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
            if getattr(request.user, 'role', None) == 'admin':
                print(4)
                return redirect('admin_main')
            return redirect('menu')
    else:
        form = LoginForm(request=request)
    # Guard against AnonymousUser lacking 'role'

    if getattr(request.user, 'role', None) == 'admin_main':
        return render(request, 'users/admin_login.html', {'form': form})
    return render(request, 'users/login.html', {'form': form, "next": request.GET.get('next', '')})

        
def login_admin(request):
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        form.error_messages = []

        if not form.clean():
            request.session.set_expiry(0)
            form.set_error('Неверный логин или пароль')
            return render(request, 'users/admin_login.html', {'form': form})

        user = form.get_user()
        if user is None:
            form.set_error('Неверный логин или пароль')
            return render(request, 'users/admin_login.html', {'form': form})

        if not (getattr(user, 'role', None) == 'admin_main' or user.is_staff or user.is_superuser):
            form.set_error('У вас нет прав администратора')
            return render(request, 'users/admin_login.html', {'form': form})

        login(request, user)

        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)

        return redirect('menu')

    else:
        form = LoginForm(request=request)

    return render(request, 'users/admin_login.html', {'form': form, "next": request.GET.get('next', '')})


@login_required
@require_POST
@csrf_protect
def topup_balance(request):
    """Пополнение баланса пользователя.

    Базовая безопасность:
    - доступно только авторизованному пользователю
    - только POST + CSRF
    - баланс не принимаем из клиента, только сумму пополнения
    - изменение баланса делаем атомарно
    """

    form = TopUpBalanceForm(request.POST)
    if not form.is_valid():
        # На этом шаге не ломаем UI: просто возвращаемся в меню.
        return redirect('menu')

    amount_cents = form.cleaned_data['amount']

    with transaction.atomic():
        user = request.user
        # SQLite не поддерживает select_for_update полноценно, но atomic всё равно защитит от частичных записей.
        user.balance_cents = int(user.balance_cents or 0) + int(amount_cents)
        user.save(update_fields=['balance_cents'])

        BalanceTopUp.objects.create(
            user=user,
            amount_cents=amount_cents,
            created_by=user,
            comment='Пополнение через интерфейс кошелька',
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        balance_display = f"{user.balance_cents // 100},{user.balance_cents % 100:02d}"
        return JsonResponse({'success': True, 'balance_cents': user.balance_cents, 'balance_display': balance_display})

    return redirect('menu')
