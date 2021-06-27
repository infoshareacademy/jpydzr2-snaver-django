from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.urls import reverse, reverse_lazy

from accounts.forms import LoginForm
from accounts.forms import SignUpForm
from project.tokens import account_activation_token

User = get_user_model()


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
            user = User.objects.get(username=raw_username)

            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string(
                'accounts/account_activation_email.html', {
                    'user': user.username,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
            user.email_user(subject, message)

            msg = f'{user.username} - account has been created'
            success = True
            return redirect('account_activation_sent')
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


def account_activation_sent(request):
    return render(request, 'accounts/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'accounts/account_activation_invalid.html')

class ProfileView(TemplateView):
    template_name = 'page-user.html'


class EmailChangeView(UpdateView):
    model = User
    fields = ['email']
    template_name = 'accounts/email_change.html'
    success_url = reverse_lazy('email_change_done')


class EmailChangeDoneView(TemplateView):
    template_name = 'accounts/email_change_done.html'