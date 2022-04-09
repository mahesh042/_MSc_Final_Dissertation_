from asyncio.windows_events import NULL
from django.shortcuts import  render, redirect
from .forms import NewUserForm,AuthenticationForm,ContactForm
from django.contrib.auth import login, authenticate,logout
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
import random,simplejson
from .models import DockStation,UserOTP
from django.core.mail import send_mail
from django.contrib import messages
from geopy.geocoders import Nominatim
from geopy.distance import  great_circle
# Create your views here.

@csrf_protect
def homepage(request):
	location_list = list(DockStation.objects.order_by('name').values()) 
	location_json = simplejson.dumps(location_list,use_decimal = True)  
	context = {'locations': location_json} 
	return render(request, 'main/home.html', context) 


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
			message = f"Hello {usr.username}\n\nTo authenticate, please enter the following one time password:\n {usr_otp} \n Thanks!"
			send_mail(
				"Welcome to Bikers Hub - Verify Your Email",
				message,
				settings.EMAIL_HOST_USER,
				[usr.email],
				fail_silently = False
				)
			return render(request, 'main/register.html', {'otp': True, 'usr': usr})		

	else:
		form = NewUserForm()
	return render(request, 'main/register.html', {'register_form':form})



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


@csrf_protect
def contact_us(request):
	if request.method == 'GET':
		form = ContactForm()
	else:
		form = ContactForm(request.POST)
		if form.is_valid():
			subject = "Contact form inquiry"
			body={
				'subject' : form.cleaned_data['subject'],
				'from_email' : form.cleaned_data['from_email'],
				'message' : form.cleaned_data['message'],
			}
			message = '\n'.join('='.join((key,val)) for (key,val) in body.items())
			sender = form.cleaned_data['from_email']
			recipient = ['bikers.den.official@gmail.com']
			try:
				send_mail(subject, message, sender,recipient,fail_silently=True)
			except BadHeaderError:
				return HttpResponse('Invalid header found.')
			return redirect('main:success')
	return render(request, "main/contact.html", {'form': form})


def successView(request):
    return render(request,'main/success.html')

def postcodesearch(request):
	return render(request,'main/postcodesearch.html')

def search(request):
	DockStation_objects = DockStation.objects.all()
	postcode = request.GET.get('postcode')
	mile_radius = request.GET.get('mile_radius')
	user_latitude = None
	user_longitude = None
	if postcode:
		geolocator = Nominatim(user_agent ='main')
		location = geolocator.geocode(postcode)
		user_latitude = location.latitude
		user_longitude = location.longitude
	output = []


	for DockStation_object in DockStation_objects:
			result = {}
			result['name'] = DockStation_object.name
			result['description'] = DockStation_object.description
			result['postcode'] = DockStation_object.postcode
			result['address'] = DockStation_object.address
			if postcode:
				initial_coords = (float(user_latitude),float(user_longitude))
				station_coords = (float(DockStation_object.latitude), float(DockStation_object.longitude))
				result['distance'] = round(great_circle(initial_coords,station_coords).miles,3)
				output.append(result)
			if mile_radius:
				if result['distance'] > int(mile_radius):
					output.pop()
	return JsonResponse(output,safe=False)




def bookings(request):
	return render(request,'main/bookings.html')
