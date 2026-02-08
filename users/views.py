from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, logout

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

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
        if form.is_valid():
            user = form.get_user()
            if user is None:
                form.set_error('Неверный логин или пароль')
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

        request.session.set_expiry(0)
        form.set_error('Неверный логин или пароль')
        print(form.error_messages)
        return render(request, 'users/login.html', {'form': form})
    else:
        form = LoginForm(request=request)
    # Guard against AnonymousUser lacking 'role'

    if getattr(request.user, 'role', None) == 'admin_main':
        return render(request, 'users/admin_login.html', {'form': form})
    return render(request, 'users/login.html', {'form': form, "next": request.GET.get('next', '')})

        
def login_admin(request):
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', None)
        if role == 'cook':
            return redirect('chef_main')
        if role == 'admin_main' or request.user.is_staff or request.user.is_superuser:
            return redirect('admin_main')
        return redirect('menu')

    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        form.error_messages = []

        if not form.is_valid():
            request.session.set_expiry(0)
            form.set_error('Неверный логин или пароль')
            return render(request, 'users/admin_login.html', {'form': form})

        user = form.get_user()
        if user is None:
            form.set_error('Неверный логин или пароль')
            return render(request, 'users/admin_login.html', {'form': form})

        role = getattr(user, 'role', None)
        if not (role in ('cook', 'admin_main') or user.is_staff or user.is_superuser):
            form.set_error('У вас нет прав для входа')
            return render(request, 'users/admin_login.html', {'form': form})

        login(request, user)

        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)

        if role == 'cook':
            return redirect('chef_main')
        return redirect('admin_main')

    form = LoginForm(request=request)
    return render(request, 'users/admin_login.html', {'form': form, "next": request.GET.get('next', '')})


@login_required
@require_POST
@csrf_protect
def topup_balance(request):

    form = TopUpBalanceForm(request.POST)
    if not form.is_valid():
        return redirect('menu')

    amount_cents = form.cleaned_data['amount']

    with transaction.atomic():
        user = request.user
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


@login_required
@require_POST
@csrf_protect
def purchase_subscription(request):

    user = request.user
    now = timezone.now()
    price_cents = 1_000_000  # 10000₽
    if user.subscription_expires_at and user.subscription_expires_at > now:
        return JsonResponse({'success': False, 'error': 'Абонемент ещё действует'}, status=400)

    current_balance = int(user.balance_cents or 0)
    if current_balance < price_cents:
        return JsonResponse({'success': False, 'error': 'Недостаточно средств'}, status=400)

    with transaction.atomic():
        user.balance_cents = current_balance - price_cents
        user.subscription_expires_at = now + timedelta(days=30)
        user.save(update_fields=['balance_cents', 'subscription_expires_at'])

    balance_display = f"{user.balance_cents // 100},{user.balance_cents % 100:02d}"
    return JsonResponse({
        'success': True,
        'balance_display': balance_display,
        'subscription_expires_at': user.subscription_expires_at.isoformat(),
    })


@require_POST
@csrf_protect
def logout_f(request):
    logout(request)
    return redirect('admin_login')


@require_POST
@csrf_protect
def logout_menu(request):
    logout(request)
    return redirect('login')
