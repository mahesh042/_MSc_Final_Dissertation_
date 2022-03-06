import email
from django.shortcuts import  render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate,logout
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import PasswordResetForm,AuthenticationForm
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
import random
from .models import UserOTP
from django.core.mail import send_mail
from django.contrib import messages
# Create your views here.
@csrf_protect
def homepage(request):
	return render(request=request, template_name='main/home.html')

@csrf_protect
def register_request(request):
	if request.method == 'POST':
		get_otp = request.POST.get('otp') #213243 #None
		if get_otp:
			get_usr = request.POST.get('usr')
			usr = User.objects.get(username=get_usr)
			if int(get_otp) == UserOTP.objects.filter(user = usr).last().otp:
				usr.is_active = True
				usr.save()
				messages.success(request, f'Account is Created For {usr.username}')
				return redirect('main:signin')
			else:
				messages.warning(request, f'You Entered a Wrong OTP')
				return render(request, 'main/register.html', {'otp': True, 'usr': usr})

		form = NewUserForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			usr = User.objects.get(username=username)
			usr.email = email
			usr.username = username
			usr.is_active = False
			usr.save()
			usr_otp = random.randint(100000, 999999)
			UserOTP.objects.create(user = usr, otp = usr_otp)

			mess = f"Hello {usr.username},\nYour OTP is {usr_otp}\nThanks!"

			send_mail(
				"Welcome to Bikers Hub - Verify Your Email",
				mess,
				settings.EMAIL_HOST_USER,
				[usr.email],
				fail_silently = False
				)

			return render(request, 'main/register.html', {'otp': True, 'usr': usr})

		
	else:
		form = NewUserForm()

	return render(request, 'main/register.html', {'register_form':form})


# def resend_otp(request):
# 	if request.method == "GET":
# 		get_usr = request.GET['usr']
# 		if User.objects.filter(username = get_usr).exists() and User.objects.get(username = get_usr).is_activev==False:
# 			usr = User.objects.get(username=get_usr)
# 			usr_otp = random.randint(100000, 999999)
# 			UserOTP.objects.create(user = usr, otp = usr_otp)
# 			mess = f"Hello {usr.first_name},\nYour OTP is {usr_otp}\nThanks!"

# 			send_mail(
# 				"Welcome to ITScorer - Verify Your Email",
# 				mess,
# 				settings.EMAIL_HOST_USER,
# 				[usr.email],
# 				fail_silently = False
# 				)
# 			return HttpResponse("Resend")

# 	return HttpResponse("Can't Send ")




			

@csrf_protect
def signin_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("main:homepage")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="main/signin.html", context={"login_form":form})

@csrf_protect
def logout_request(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect("main:homepage")

@csrf_protect
def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "main/password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:

						return HttpResponse('Invalid header found.')
						
					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return redirect ("main:homepage")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="main/password/password_reset.html", context={"password_reset_form":password_reset_form})
