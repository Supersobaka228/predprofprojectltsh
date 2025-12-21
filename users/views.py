from django.shortcuts import render, redirect
from .forms import RegisterForm

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