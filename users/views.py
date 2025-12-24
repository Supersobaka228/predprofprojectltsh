from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from .forms import RegisterForm, LoginForm


# Create your views here.
def register(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        form = RegisterForm(request.POST)
        if form.is_valid():
            print(113)
            form.save()
            return redirect('admin')
        else:
            print(form.errors)
            error = 'Форма неверна'
    form = RegisterForm()
    data = {'form': form}
    print(form)
    return render(request, 'users/register.html', data)



def login(request):
    if request.method == "POST":

        form = LoginForm(request=request, data=request.POST)
        print(form.errors)
        if form.is_bound:
            user = form.get_user()
            print(form.clean)
            f = form.get_remember_me()
            if not f:
                request.session.set_expiry(0)

            print(f)

            # Получаем параметр next
            next_url = request.POST.get('next') or request.GET.get('next')

            if next_url:
                return redirect(next_url)
            return redirect('menu')
    else:
        form = LoginForm(request=request)

    return render(request, 'users/login.html', {'form': form, "next": request.GET.get('next', '')})

        

