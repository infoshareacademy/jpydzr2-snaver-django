from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from accounts.forms import LoginForm, SignUpForm


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def registration_view(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            raw_username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=raw_username, password=raw_password)

            msg = f'{user.username} - account has been created'
            success = True
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    context = {
        "form": form,
        "msg": msg,
        "success": success,
    }

    return render(request, "accounts/register.html", context=context)
