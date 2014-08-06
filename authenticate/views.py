# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.db import transaction
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from authenticate.forms import RegistrationForm, LoginForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from django.db import models

from events.models import GeoLocUser

FROM_EMAIL = "eventfinder.cmu@gmail.com"
my_domain = "ec2-54-191-107-23.us-west-2.compute.amazonaws.com"

@transaction.commit_on_success
def signin(request):
    context = {}
    errors = []
    context['errors'] = errors
    context['reg_form'] = RegistrationForm()

    if request.method == 'GET':
        context['login_form'] = LoginForm()
        return render(request, 'authenticate/index.html', context)

    form = LoginForm(request.POST)
    context['login_form'] = form

    #Validates the form
    if not form.is_valid():
        return render(request, 'authenticate/index.html', context)


    # User valid, Log them in
    user = authenticate(username=form.cleaned_data['username'], \
                        password=form.cleaned_data['password1'])
    if (user.is_active):
        login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        context['errors'] = ['Cannot login until you have verified your account.']
        return render(request, 'authenticate/index.html', context)

@transaction.commit_on_success
def custom_login(request):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return signin(request)

@transaction.commit_on_success
def register(request):
    context = {}
    errors = []
    context['errors'] = errors
    context['login_form'] = LoginForm()


    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        context['reg_form'] = RegistrationForm()
        return render(request, 'authenticate/index.html', context)


    form = RegistrationForm(request.POST)
    context['reg_form'] = form

    if not form.is_valid():
        return render(request, 'authenticate/index.html', context)

    # Creates the new user from the valid form data
    new_user_auth = User.objects.create_user(username=form.cleaned_data['username'], \
                                        password=form.cleaned_data['password1'],\
                                        first_name=form.cleaned_data['name'])
    new_user_auth.is_active = False
    new_user_auth.save()
    new_user = GeoLocUser(user=new_user_auth)
    new_user.save()
    tok = default_token_generator.make_token(new_user.user)
    email_body = ("Welcome to EventFinder! Please verify your account by clicking this link. This will redirect you to"
                   "our login page, where you can login with your username and password:"
                   "%s/%s/%s/%s" % (my_domain, 'authenticate/confirm-registration', new_user_auth.username, tok))
    send_mail(subject="Verify your EventFinder Account",
              message=email_body,
              from_email=FROM_EMAIL,
              recipient_list=[new_user_auth.username])
    context['user'] = new_user
    return render(request, 'authenticate/needs_confirmation.html', context)


@transaction.commit_on_success
def confirm_registration(request, username, token):
	auth_user = get_object_or_404(User, username=username)

	# Send 404 error if token is invalid
	if not default_token_generator.check_token(auth_user, token):
		raise Http404("Invalid authentication token. Please check your email again.")

	# Otherwise token was valid, activate the user.
	auth_user.is_active = True
	auth_user.save()
	return redirect(settings.LOGIN_REDIRECT_URL)

def custom_register(request):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return register(request)

def reset(request):
    context = {}
    errors = []
    context['errors'] = errors

    if request.method == 'GET':
        return render(request, 'authenticate/reset.html', context)

    if 'email' not in request.POST or not request.POST['email']:
        errors.append("Must specify an email.")
    else:
        if len(User.objects.filter(username = request.POST['email'])) == 0:
            errors.append('%s is not a registered user.' % request.POST['email'])
        else:
            context['username'] = request.POST['email']

    if errors:
        return render(request, 'authenticate/reset.html',context)

    new_password = User.objects.make_random_password()
    user = get_object_or_404(User, username=context['username'])
    user.set_password(new_password)
    user.save()
    #Gives user a new password and sends it in a message to their email
    email_body = """
        Here is your new temporary password: %s. Be sure to change it once you login by clicking your name, then 'Change Password'.""" % new_password
    send_mail(subject="Password reset.",
              message=email_body,
              from_email=FROM_EMAIL,
              recipient_list=[context['username']])
    return redirect('/authenticate/index.html')


def change_password(request):
    context = {}
    errors = []
    context['errors'] = errors
    if request.method == 'GET':
        context['form'] = PasswordChangeForm()
        return render(request, 'authenticate/change_password.html', context)

    form = PasswordChangeForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'authenticate/change_password.html', context)

    else:
        request.user.set_password(form.cleaned_data['password'])
        request.user.save()
        return render(request, 'authenticate/change_password.html', context)
